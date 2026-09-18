from dataclasses import dataclass

from app.analysis.hashing import hamming_distance
from app.config import HASH_DISTANCE_THRESHOLD


@dataclass
class PhotoForGrouping:
    id: str
    phash: str
    blur_score: float | None
    eyes_state: str | None


@dataclass
class GroupingResult:
    group_id: str | None
    is_recommended_keeper: bool | None


class _UnionFind:
    """Standard union-find (disjoint set) with path compression: each
    photo starts as its own group, and every near-duplicate pair we find
    merges their groups together, so a burst of 4 near-identical shots
    ends up as one group even if we only directly compared some pairs.
    """

    def __init__(self, ids: list[str]):
        self.parent = {photo_id: photo_id for photo_id in ids}

    def find(self, x: str) -> str:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x: str, y: str) -> None:
        root_x, root_y = self.find(x), self.find(y)
        if root_x != root_y:
            self.parent[root_x] = root_y


def _keeper_sort_key(photo: PhotoForGrouping) -> tuple[int, float]:
    eyes_open = 1 if photo.eyes_state == "open" else 0
    return (eyes_open, photo.blur_score or 0.0)


def group_photos(
    photos: list[PhotoForGrouping],
    distance_threshold: int = HASH_DISTANCE_THRESHOLD,
) -> dict[str, GroupingResult]:
    """Cluster near-duplicate photos by perceptual hash distance, and
    within each cluster recommend a keeper: the sharpest photo with eyes
    open, falling back to the sharpest photo overall if none qualify.
    Photos with no near-duplicates get group_id=None (not part of a burst).
    """
    union_find = _UnionFind([photo.id for photo in photos])

    for i in range(len(photos)):
        for j in range(i + 1, len(photos)):
            if hamming_distance(photos[i].phash, photos[j].phash) <= distance_threshold:
                union_find.union(photos[i].id, photos[j].id)

    clusters: dict[str, list[PhotoForGrouping]] = {}
    for photo in photos:
        root = union_find.find(photo.id)
        clusters.setdefault(root, []).append(photo)

    results: dict[str, GroupingResult] = {}
    for members in clusters.values():
        if len(members) == 1:
            results[members[0].id] = GroupingResult(group_id=None, is_recommended_keeper=None)
            continue

        group_id = min(photo.id for photo in members)  # stable, deterministic id
        keeper = max(members, key=_keeper_sort_key)
        for photo in members:
            results[photo.id] = GroupingResult(
                group_id=group_id,
                is_recommended_keeper=photo.id == keeper.id,
            )

    return results
