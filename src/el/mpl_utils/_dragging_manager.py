"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
18.01.25, 16:36

Object dragging management across an entire canvas that prevents overlapping
objects from being dragged together and adds some other features compared to the 
built-in Draggables in matplotlib.
Closely inspired by matplotlib.offsetbox.DraggableBase and this post:
https://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively
Also supports blitting (like the builtin implementation) to improve performance:
https://matplotlib.org/stable/users/explain/animations/blitting.html
"""

import typing
import dataclasses

from ._deps import *


@dataclasses.dataclass
class DraggableArtistEntry:
    artist: mpl_artist.Artist
    on_drag_start: typing.Callable[[], bool] | None
    pos_validator: typing.Callable[[tuple[int, int], tuple[int, int]], tuple[int, int]] | None
    on_drag_end: typing.Callable[[], bool] | None


class DraggingManger:

    def __init__(self, canvas: mpl_bases.FigureCanvasBase | None = None, use_blit: bool = False):
        # the canvas this manager operates on
        self._canvas: mpl_bases.FigureCanvasBase | None = None

        # whether we would like to use blitting
        self._want_to_use_blit: bool = use_blit
        # whether blitting is actually enabled (depending on canvas)
        self._use_blit: bool = False
        # background store when using blit. Don't quite know what the type of this is supposed to be
        self._background: typing.Any = ...

        # all artist managed by this manager
        self._artists: dict[mpl_artist.Artist, DraggableArtistEntry] = {}
        # the artist currently being dragged
        self._current_element: DraggableArtistEntry | None = None

        # mouse and artist starting positions of drag to calculate deltas
        self._mouse_start_x: int = 0 
        self._mouse_start_y: int = 0 
        self._artist_start_x: int = 0 
        self._artist_start_y: int = 0 
        self._artist_start_transformed_x: int = 0 
        self._artist_start_transformed_y: int = 0 

        # callback id's 
        self._cids: list[int] = []

        if canvas is not None:
            self.connect_to_canvas(canvas)

    def connect_to_canvas(self, new_canvas: mpl_bases.FigureCanvasBase) -> None:
        if self._canvas is not None:
            self.disconnect_from_canvas()
        self._canvas = new_canvas
        # enable blitting if requested and supported
        self._use_blit = self._want_to_use_blit and self._canvas.supports_blit
        # connect to events
        self._cids.append(self._canvas.mpl_connect('button_release_event', self._drag_on_release))
        self._cids.append(self._canvas.mpl_connect('pick_event', self._drag_on_pick))
        self._cids.append(self._canvas.mpl_connect('motion_notify_event', self._drag_on_motion))
    
    def disconnect_from_canvas(self) -> None:
        if self._canvas is not None:
            for cid in self._cids:
                self._canvas.mpl_disconnect(cid)
            self._canvas = None
            self._use_blit = False

    def register_artist(
        self, 
        artist: mpl_artist.Artist,
        on_drag_start: typing.Callable[[], bool] | None = None,
        pos_validator: typing.Callable[[tuple[int, int], tuple[int, int]], tuple[int, int]] | None = None,
        on_drag_end: typing.Callable[[], bool] | None = None
    ) -> None:
        """
        Registers an artist to be made draggable.

        Parameters
        ----------
        artist : mpl_artist.Artist
            The artist to make draggable. This must be a supported artist type
            whose position can be read and set
        on_drag_start : typing.Callable[[], bool] | None, optional
            Callback indicating dragging is about to start (artist picked), by default None.
            If this callback is provided, it must return True to accept a drag.
            If it returns false, the drag is aborted. This way dragging can be dynamically and
            temporarily disabled by external factors.
        pos_validator : typing.Callable[[tuple[int, int], tuple[int, int]], tuple[int, int]] | None, optional
            Position validator function. This is called for every movement during a drag to
            validate the new position the element is moved to. This is useful for limiting
            the movement of the artist to some range or direction.
            Parameters:
                tuple[int, int]: starting position of the artist before the drag (in artist coordinate system)
                tuple[int, int]: the current target position the artist would be moved to by the drag (in artist coordinate system)
            Return Value:
                tuple[int, int]: the (possibly modified) target position the artist should really be moved to
        on_drag_end : typing.Callable[[], bool] | None, optional
            Callback indicating dragging is about to end (artist released), by default None
            If this callback is provided, it must return True to accept a drag.
            If it returns false, the drag is aborted and the artist will be moved back to the starting position.
        """

        if artist in self._artists:
            return
        else:
            if not artist.pickable():
                # save the old pickable state (bit of pfusch) to restore it later
                artist._dm_was_previously_pickable = artist.pickable()
                artist.set_picker(True)
            self._artists[artist] = DraggableArtistEntry(
                artist=artist,
                on_drag_start=on_drag_start,
                pos_validator=pos_validator,
                on_drag_end=on_drag_end
            )

    def unregister_artist(self, artist: mpl_artist.Artist) -> None:
        if artist in self._artists:
            del self._artists[artist]
            # restore previous pickable state
            if hasattr(artist, "_dm_was_previously_pickable"):
                artist.set_picker(artist._dm_was_previously_pickable)

    def _drag_on_pick(self, event: mpl_bases.PickEvent) -> None:
        if self._canvas is None:
            return
        if event.artist in self._artists and self._current_element is None:
            # run cb if defined
            if self._artists[event.artist].on_drag_start is not None:
                if not self._artists[event.artist].on_drag_start():
                    return  # return if callback aborts drag
            self._current_element = self._artists[event.artist]
            self._mouse_start_x = event.mouseevent.x
            self._mouse_start_y = event.mouseevent.y
            self._save_artist_starting_position()
            # prepare blitting if enabled
            if self._use_blit:
                self._current_element.artist.set_animated(True) # disable auto drawing of the target
                self._canvas.draw() # draw the background
                # save background, only available on blitting supporting backends
                self._background = self._canvas.copy_from_bbox(self._current_element.artist.get_figure().bbox)
                # restore the background (otherwise the artist disappears if not moved for some reason)
                self._canvas.restore_region(self._background)
                self._current_element.artist.draw(self._current_element.artist.get_figure()._get_renderer())    # manually draw the artist
                self._canvas.blit() # update the screen

    def _drag_on_motion(self, event: mpl_bases.MouseEvent) -> None:
        if self._canvas is None:
            return
        if self._current_element is not None:
            # calculate the deltas from start position
            dx = event.x - self._mouse_start_x
            dy = event.y - self._mouse_start_y
            self._set_artist_offset(dx, dy)
            if self._use_blit:
                # re-use the background
                self._canvas.restore_region(self._background)
                # manually re-draw only the artist
                self._current_element.artist.draw(self._current_element.artist.get_figure()._get_renderer())
                # update screen
                self._canvas.blit()
            else:
                # just draw normally if blitting is disabled
                self._canvas.draw()

    def _drag_on_release(self, event: mpl_bases.MouseEvent) -> None:
        if self._canvas is None:
            return
        if self._current_element is not None:
            dx = event.x - self._mouse_start_x
            dy = event.y - self._mouse_start_y

            # run cb if defined
            if self._current_element.on_drag_end is not None:
                if self._current_element.on_drag_end(): # if cb returns True the drag is accepted
                    self._set_artist_offset(dx, dy)
                    self._finalize_artist_drag()
                else:
                    self._set_artist_offset(0, 0)      # drag rejected, go back to initial position
            else:
                self._set_artist_offset(dx, dy)
                self._finalize_artist_drag()

            self._current_element.artist.set_animated(False)    # back to normal rendering again 
            self._current_element = None

    def _save_artist_starting_position(self) -> None:
        if isinstance(self._current_element.artist, mpl_text.Annotation):
            # the draggable part is the text annotation element, not the target position.
            self._artist_start_transformed_x, self._artist_start_transformed_y = self._current_element.artist.xyann
            # We get the absolute screen coordinates using the annotation transform
            self._artist_start_x, self._artist_start_y = self._current_element.artist.get_transform().transform(self._current_element.artist.xyann)
        # implement more elements here if required

    def _set_artist_offset(self, dx: int, dy: int) -> None:
        """ Moves the artist ot an offset from it's starting position """
        if isinstance(self._current_element.artist, mpl_text.Annotation):
            # transform the absolute coordinates back to annotation coordinate system
            target_x, target_y = self._current_element.artist.get_transform().inverted().transform((
                self._artist_start_x + dx,
                self._artist_start_y + dy
            ))
            # apply validator if defined
            if self._current_element.pos_validator is not None:
                target_x, target_y = self._current_element.pos_validator(
                    (self._artist_start_transformed_x, self._artist_start_transformed_y),
                    (target_x, target_y)
                )
            self._current_element.artist.xyann = (target_x, target_y)
        # implement more required types here
    
    def _finalize_artist_drag(self) -> None:
        """
        Called when drag is finished by releasing. Can be used
        to do some final position calculations or checks
        """
        # for now we don't need this
