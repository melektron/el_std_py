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

from ._deps import *

DragCheckCB = typing.Callable[[], bool]
PosValidatorCB = typing.Callable[[tuple[int, int], tuple[int, int]], tuple[int, int]]

class DraggableArtistEntry:

    def __init__(
        self,
        artist: mpl_artist.Artist,
        on_drag_start: DragCheckCB | None = None,
        pos_validator: PosValidatorCB | None = None,
        on_drag_end: DragCheckCB | None = None,
    ):
        """
        Representation of a draggable artist with all required data.

        Parameters
        ----------
        artist : `mpl_artist.Artist`
            The artist to make draggable. Subtypes will specialize this
        on_drag_start : `typing.Callable[[], bool] | None`, optional
            Callback indicating dragging is about to start (artist picked), by default None.
            If this callback is provided, it must return True to accept a drag.
            If it returns false, the drag is aborted. This way dragging can be dynamically and
            temporarily disabled by external factors.
        pos_validator : `typing.Callable[[tuple[int, int], tuple[int, int]], tuple[int, int]] | None`, optional
            Position validator function. This is called for every movement during a drag to
            validate the new position the element is moved to. This is useful for limiting
            the movement of the artist to some range or direction.

            *Parameters*:
                tuple[int, int]: starting position of the artist before the drag (in artist coordinate system)
                tuple[int, int]: the current target position the artist would be moved to by the drag (in artist coordinate system)
            *Return Value*:
                tuple[int, int]: the (possibly modified) target position the artist should really be moved to

        on_drag_end : `typing.Callable[[], bool] | None`, optional
            Callback indicating dragging is about to end (artist released), by default None
            If this callback is provided, it must return True to accept a drag.
            If it returns false, the drag is aborted and the artist will be moved back to the starting position.
        """
        self.artist = artist
        self.on_drag_start = on_drag_start
        self.pos_validator = pos_validator
        self.on_drag_end = on_drag_end

    def save_artist_starting_position(self) -> None:
        """
        Called on drag start to save the starting position.
        To be overwritten by artist-specific implementation.
        """

    def set_artist_offset(self, dx: int, dy: int) -> None:
        """
        Called whenever the artist is to be moved to a new position
        represented as an offset from the starting position in pixels.
        To be overwritten by artist-specific implementation.
        """
    
    def finalize_artist_drag(self) -> None:
        """
        Called when drag is finished by releasing. Can be used
        to do some final position calculations or checks.
        """


class DraggableAnnotationEntry(DraggableArtistEntry):

    def __init__(
        self,
        annotation: mpl_text.Annotation,
        move_target: bool = False,  # whether we want to move the target position. by default we move the text position. (only works on backends that support get_renderer())
        on_drag_start: DragCheckCB | None = None,
        pos_validator: PosValidatorCB | None = None,
        on_drag_end: DragCheckCB | None = None,
    ):
        super().__init__(annotation, on_drag_start, pos_validator, on_drag_end)
        self.artist: mpl_text.Annotation
        self._move_target = move_target
        self._start_x: int = 0 
        self._start_y: int = 0 
        self._start_transformed_x: int = 0 
        self._start_transformed_y: int = 0 

    @typing.override
    def save_artist_starting_position(self) -> None:
        # select target or text position depending on config
        if self._move_target:
            coords = self.artist.xy
            # we need to abuse some internal functions to get the target point transform
            # See mpl text.py@1470 (at least at the time of writing) for the _get_xy_transform function
            # we also need the renderer which we really should not have. We need to get it some way,
            # this only works on some backends, such as TkAgg
            # https://stackoverflow.com/questions/60678571/how-do-i-obtain-a-matplotlib-renderer-to-pass
            trans = self.artist._get_xy_transform(self.artist.get_figure().canvas.get_renderer(), self.artist.xycoords)
        else:
            coords = self.artist.xyann
            trans = self.artist.get_transform()
        # the draggable part is the text annotation element, not the target position.
        self._start_transformed_x, self._start_transformed_y = coords
        # We get the absolute screen coordinates using the annotation transform
        self._start_x, self._start_y = trans.transform(coords)

    @typing.override
    def set_artist_offset(self, dx: int, dy: int) -> None:
        # select target or text transform depending on config
        if self._move_target:
            # we need to abuse some internal functions to get the target point transform
            # See mpl text.py@1470 (at least at the time of writing) for the _get_xy_transform function
            # we also need the renderer which we really should not have. We need to get it some way,
            # this only works on some backends, such as TkAgg
            # https://stackoverflow.com/questions/60678571/how-do-i-obtain-a-matplotlib-renderer-to-pass
            trans = self.artist._get_xy_transform(self.artist.get_figure().canvas.get_renderer(), self.artist.xycoords)
        else:
            trans = self.artist.get_transform()

        # transform the absolute coordinates back to annotation coordinate system
        target_x, target_y = trans.inverted().transform((
            self._start_x + dx,
            self._start_y + dy
        ))
        # apply validator if defined
        if self.pos_validator is not None:
            target_x, target_y = self.pos_validator(
                (self._start_transformed_x, self._start_transformed_y),
                (target_x, target_y)
            )
        
        # change target or text position depending on config
        if self._move_target:
            self.artist.xy = (target_x, target_y)
        else:
            self.artist.xyann = (target_x, target_y)


class DraggableOffsetBoxEntry(DraggableArtistEntry):

    def __init__(
        self,
        artist: mpl_artist.Artist,
        offsetbox: mpl_off.OffsetBox,
        on_drag_start: DragCheckCB | None = None,
        pos_validator: PosValidatorCB | None = None,
        on_drag_end: DragCheckCB | None = None,
    ):
        super().__init__(artist, on_drag_start, pos_validator, on_drag_end)
        self.offsetbox = offsetbox
        self._start_x: int = 0 
        self._start_y: int = 0 
        self._start_transformed_x: int = 0 
        self._start_transformed_y: int = 0 

    @typing.override
    def save_artist_starting_position(self) -> None:
        renderer = self.offsetbox.get_figure()._get_renderer()
        # We get the absolute screen coordinates using the annotation transform
        self._start_x, self._start_y = self.offsetbox.get_offset(
            self.offsetbox.get_bbox(renderer), renderer
        )
        # idk why this is needed but the official implementation does it as well (see offsetbox.py@1542)
        self.offsetbox.set_offset((self._start_x, self._start_y))

    @typing.override
    def set_artist_offset(self, dx: int, dy: int) -> None:
        # offsetbox has not transform, we always operate on absolute coords
        target_pos = (
            self._start_x + dx,
            self._start_y + dy
        )
        # apply validator if defined
        if self.pos_validator is not None:
            target_x, target_y = self.pos_validator(
                (self._start_x, self._start_x),
                (target_x, target_y)
            )
        self.offsetbox.set_offset(target_pos)

    def get_loc_in_canvas(self) -> tuple:
        # This has been taken from matplotlib's DraggableOffsetBox implementation,
        # don't really understand what this does and why it doesn't use the normal get_offset() method
        renderer = self.offsetbox.get_figure()._get_renderer()
        bbox = self.offsetbox.get_bbox(renderer)
        ox, oy = self.offsetbox._offset
        loc_in_canvas = (ox + bbox.x0, oy + bbox.y0)
        return loc_in_canvas


class DraggableLegendEntry(DraggableOffsetBoxEntry):

    def __init__(
        self,
        legend: mpl_legend.Legend,
        update: typing.Literal["loc", "bbox"] = "loc",
        on_drag_start: DragCheckCB | None = None,
        pos_validator: PosValidatorCB | None = None,
        on_drag_end: DragCheckCB | None = None,
    ):
        """
        Entry for matplotlibs `Legend` to support dragging.
        This supports everything from the official dragging implementation
        but adds the features of the DraggingManager.

        Parameters
        ----------
        legend : `Legend`
            The `Legend` instance to wrap.
        update : {'loc', 'bbox'}, optional
            If "loc", update the *loc* parameter of the legend upon finalizing.
            If "bbox", update the *bbox_to_anchor* parameter.
        """
        super().__init__(legend, legend._legend_box, on_drag_start, pos_validator, on_drag_end)
        self.artist: mpl_legend.Legend
        self._update: typing.Literal["loc", "bbox"] = update

    @typing.override
    def finalize_artist_drag(self):
        if self._update == "loc":
            self._update_loc(self.get_loc_in_canvas())
        elif self._update == "bbox":
            self._update_bbox_to_anchor(self.get_loc_in_canvas())

    def _update_loc(self, loc_in_canvas):
        bbox = self.artist.get_bbox_to_anchor()
        # if bbox has zero width or height, the transformation is
        # ill-defined. Fall back to the default bbox_to_anchor.
        if bbox.width == 0 or bbox.height == 0:
            self.artist.set_bbox_to_anchor(None)
            bbox = self.artist.get_bbox_to_anchor()
        bbox_transform = mpl_trans.BboxTransformFrom(bbox)
        self.artist._loc = tuple(bbox_transform.transform(loc_in_canvas))

    def _update_bbox_to_anchor(self, loc_in_canvas):
        loc_in_bbox = self.artist.axes.transAxes.transform(loc_in_canvas)
        self.artist.set_bbox_to_anchor(loc_in_bbox)


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
        self._artist_entries: dict[mpl_artist.Artist, DraggableArtistEntry] = {}
        # the artist currently being dragged
        self._current_entry: DraggableArtistEntry | None = None

        # mouse starting positions of drag to calculate deltas
        self._mouse_start_x: int = 0 
        self._mouse_start_y: int = 0 

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

    def register_artist(self, entry: DraggableArtistEntry) -> None:
        """Registers an artist to be made draggable.

        Parameters
        ----------
        entry : `DraggableArtistEntry`
            An object of a subclass of `DraggableArtistEntry` that implements
            the dragging functionality for a specific artist type.
            currently supported:
              - DraggableAnnotationEntry
              - DraggableOffsetBoxEntry
              - DraggableLegendEntry
        """

        if entry.artist in self._artist_entries:
            return
        if not entry.artist.pickable():
            # save the old pickable state (bit of pfusch) to restore it later
            entry.artist._dm_was_previously_pickable = entry.artist.pickable()
            entry.artist.set_picker(True)

        self._artist_entries[entry.artist] = entry

    def unregister_artist(self, artist: mpl_artist.Artist) -> None:
        if artist in self._artist_entries:
            del self._artist_entries[artist]
            # restore previous pickable state
            if hasattr(artist, "_dm_was_previously_pickable"):
                artist.set_picker(artist._dm_was_previously_pickable)

    def _drag_on_pick(self, event: mpl_bases.PickEvent) -> None:
        if self._canvas is None:
            return
        if event.artist in self._artist_entries and self._current_entry is None:
            # run cb if defined
            if self._artist_entries[event.artist].on_drag_start is not None:
                if not self._artist_entries[event.artist].on_drag_start():
                    return  # return if callback aborts drag
            self._current_entry = self._artist_entries[event.artist]
            self._mouse_start_x = event.mouseevent.x
            self._mouse_start_y = event.mouseevent.y
            self._current_entry.save_artist_starting_position()
            # prepare blitting if enabled
            if self._use_blit:
                self._current_entry.artist.set_animated(True) # disable auto drawing of the target
                self._canvas.draw() # draw the background
                # save background, only available on blitting supporting backends
                self._background = self._canvas.copy_from_bbox(self._current_entry.artist.get_figure().bbox)
                # restore the background (otherwise the artist disappears if not moved for some reason)
                self._canvas.restore_region(self._background)
                self._current_entry.artist.draw(self._current_entry.artist.get_figure()._get_renderer())    # manually draw the artist
                self._canvas.blit() # update the screen

    def _drag_on_motion(self, event: mpl_bases.MouseEvent) -> None:
        if self._canvas is None:
            return
        if self._current_entry is not None:
            # calculate the deltas from start position
            dx = event.x - self._mouse_start_x
            dy = event.y - self._mouse_start_y
            self._current_entry.set_artist_offset(dx, dy)
            if self._use_blit:
                # re-use the background
                self._canvas.restore_region(self._background)
                # manually re-draw only the artist
                self._current_entry.artist.draw(self._current_entry.artist.get_figure()._get_renderer())
                # update screen
                self._canvas.blit()
            else:
                # just draw normally if blitting is disabled
                self._canvas.draw()

    def _drag_on_release(self, event: mpl_bases.MouseEvent) -> None:
        if self._canvas is None:
            return
        if self._current_entry is not None:
            dx = event.x - self._mouse_start_x
            dy = event.y - self._mouse_start_y

            # run cb if defined
            if self._current_entry.on_drag_end is not None:
                if self._current_entry.on_drag_end(): # if cb returns True the drag is accepted
                    self._current_entry.set_artist_offset(dx, dy)
                    self._current_entry.finalize_artist_drag()
                else:
                    self._current_entry.set_artist_offset(0, 0)      # drag rejected, go back to initial position
            else:
                self._current_entry.set_artist_offset(dx, dy)
                self._current_entry.finalize_artist_drag()

            self._current_entry.artist.set_animated(False)    # back to normal rendering again 
            self._canvas.draw()     # draw the entire canvas once to guarantee proper z-ordering
            self._current_entry = None
            self._background = None # make sure this object does not remain as it sometimes causes problems



