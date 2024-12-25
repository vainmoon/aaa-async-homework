import asyncio
from typing import Coroutine


async def limit_execution_time(coro: Coroutine, max_execution_time: float) -> None:
    # Функция принимает на вход корутину, которую необходимо запустить, однако иногда она выполняется
    # слишком долго, это время необходимо ограничить переданным на вход количеством секунд.
    #
    # Тест проверяет, что каждая переданная корутина была запущена, и все они завершились за заданное
    # время.
    #

    try:
        async with asyncio.timeout(max_execution_time):
            await coro

    except asyncio.TimeoutError:
        return


async def limit_execution_time_many(*coros: Coroutine, max_execution_time: float) -> None:
    # Функция эквивалентна limit_execution_time, но корутин на вход приходит несколько.

    tasks = [asyncio.create_task(coro) for coro in coros]

    done, pending = await asyncio.wait(tasks, timeout=max_execution_time)
    for t in pending:
        t.cancel()
