import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count


def _factorize_one(n):
    result = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            result.append(i)
            if i != n // i:
                result.append(n // i)
        i += 1
    return sorted(result)


def factorize_sync(*numbers):
    return [_factorize_one(n) for n in numbers]


def factorize(*numbers):
    with ProcessPoolExecutor(max_workers=cpu_count()) as pool:
        return list(pool.map(_factorize_one, numbers))


def check(func):
    a, b, c, d = func(128, 255, 99999, 10651060)
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316,
                 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]


if __name__ == "__main__":
    check(factorize_sync)
    check(factorize)

    nums = (128, 255, 99999, 10651060, 10**13 + 37, 10**13 + 39, 10**13 + 41, 10**13 + 43, 10**13 + 47, 10**13 + 49, 10**13 + 51, 10**13 + 53)
    for name, func in (("sync", factorize_sync), ("parallel", factorize)):
        start = time.perf_counter()
        func(*nums)
        print(f"{name}: {time.perf_counter() - start:.3f}s")
    print(f"cpu_count = {cpu_count()}")
