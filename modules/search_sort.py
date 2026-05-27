"""
modules/search_sort.py
Lab 4 — Sorting (Bubble / Selection) and Searching (Linear / Binary)
"""


# ── Sorting Algorithms ────────────────────────────────────────────────────────

def bubble_sort(items: list, key: str) -> list:
    """Sorts list of dicts in-place by key using Bubble Sort."""
    arr = [dict(r) for r in items]          # shallow copy
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            val_j  = str(arr[j][key]).lower()
            val_j1 = str(arr[j + 1][key]).lower()
            # Try numeric comparison first
            try:
                val_j, val_j1 = float(arr[j][key]), float(arr[j + 1][key])
            except (ValueError, TypeError):
                pass
            if val_j > val_j1:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def selection_sort(items: list, key: str) -> list:
    """Sorts list of dicts using Selection Sort."""
    arr = [dict(r) for r in items]
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            val_min = str(arr[min_idx][key]).lower()
            val_j   = str(arr[j][key]).lower()
            try:
                val_min, val_j = float(arr[min_idx][key]), float(arr[j][key])
            except (ValueError, TypeError):
                pass
            if val_j < val_min:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


# ── Search Algorithms ─────────────────────────────────────────────────────────

def linear_search(items: list, key: str, target: str) -> int:
    """Returns first index where items[i][key] matches target, else -1."""
    for i, item in enumerate(items):
        if str(item.get(key, "")).lower() == target.lower():
            return i
    return -1


def binary_search(sorted_items: list, key: str, target: str) -> int:
    """
    Binary search on a pre-sorted list of dicts.
    Returns index if found, else -1.
    """
    low, high = 0, len(sorted_items) - 1
    target_lower = target.lower()

    while low <= high:
        mid = (low + high) // 2
        mid_val = str(sorted_items[mid].get(key, "")).lower()

        # Try numeric comparison
        try:
            mid_val_n = float(sorted_items[mid][key])
            target_n  = float(target)
            if mid_val_n == target_n:
                return mid
            elif mid_val_n < target_n:
                low = mid + 1
            else:
                high = mid - 1
        except (ValueError, TypeError):
            if mid_val == target_lower:
                return mid
            elif mid_val < target_lower:
                low = mid + 1
            else:
                high = mid - 1

    return -1
