import json
import typing


class BaseDataClass:
    """
    Base class for all data classes.
    """

    def __init__(self, js):
        self.raw = js

        for k, v in js.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return isinstance(other, BaseDataClass) and self.raw == other.raw

    def __hash__(self):
        return hash(json.dumps(self.raw))


class Track(BaseDataClass):
    """A specific spotify track"""

    def __eq__(self, other):
        try:
            return isinstance(other, Track) and self.raw['id'] == other.raw['id']
        except KeyError:
            try:
                return isinstance(other, Track) and self.id == other.id
            except:
                return super().__eq__(other)

    def __repr__(self):
        try:
            return f"<Track id={self.id}>"
        except:
            return super().__repr__()


class CurrentUser(BaseDataClass):
    """The current user's information"""
    pass


class CreatedPlaylist(BaseDataClass):
    """A playlist that has been created"""
    pass


class AddItemToPlaylist(BaseDataClass):
    """The API response object for the item that has been added to a playlist"""
    pass


class DeleteItemFromPlaylist(BaseDataClass):
    """The API response object for the item that has been added to a playlist"""
    pass


class CurrentUserPlaylists(BaseDataClass):
    """The current user's playlists"""
    pass


class PlaylistItems(BaseDataClass):
    """A list of playlist items/tracks"""

    def __init__(self, js):
        super().__init__(js)

        self.items = []

        for item in js["items"]:
            flag = True

            for k, v in item.items():
                try:
                    if k == 'track':
                        item[k] = Track(v)
                    else:
                        item[k] = v
                except:
                    flag = False
                    break

            if flag:
                self.items.append(item)
