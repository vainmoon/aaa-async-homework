import abc
import asyncio
from typing import Coroutine, Set


class AbstractLongTaskCreator:
    # Этот класс реализован в тестах, вам не нужно его трогать.
    @abc.abstractmethod
    def create_long_task(self) -> Coroutine:
        ...


class BackgroundCoroutinesWatcher:
    def __init__(self):
        self._running_tasks: Set[asyncio.Task] = set()

    def schedule_soon(self, coro: Coroutine):
        task = asyncio.create_task(coro)
        self._running_tasks.add(task)
        task.add_done_callback(self._remove_from_running_task)

    def _remove_from_running_task(self, task: asyncio.Task) -> None:
        self._running_tasks.remove(task)

    async def close(self):
        # Здесь необходимо реализовать отмену корутин, которые ещё не успели завершиться.
        close_task = set(self._running_tasks)
        for task in close_task:
            if not task.done():
                self._remove_from_running_task(task)
                task.cancel()


class FastHandlerWithLongBackgroundTask:
    def __init__(self, long_task_creator: AbstractLongTaskCreator, bcw: BackgroundCoroutinesWatcher):
        self._long_task_creator = long_task_creator
        self._bcw = bcw

    async def handle_request(self) -> None:
        # Тест вызывает этот метод и проверяет что корутина была запланирована
        # и начала исполняться, а хендлер завершил работу за ожидаемое время.
        coro = self._long_task_creator.create_long_task()
        self._bcw.schedule_soon(coro)

    async def close(self) -> None:
        # Этот метод будет вызван при завершении работы, все незавершённые корутины
        # полученные из create_long_task, должны быть отменены.
        await self._bcw.close()
