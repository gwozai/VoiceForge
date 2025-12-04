"""请求队列管理器"""

import threading
import time
import queue
from typing import Optional, Callable, Any
from dataclasses import dataclass
from ..utils.logger import LoggerMixin


@dataclass
class QueueTask:
    """队列任务"""
    task_id: str
    func: Callable
    args: tuple
    kwargs: dict
    callback: Optional[Callable] = None
    priority: int = 0  # 优先级，数字越小优先级越高


class RequestQueueManager(LoggerMixin):
    """请求队列管理器 - 确保语音服务器请求的同步处理"""
    
    def __init__(self, max_workers: int = 1):
        """
        初始化队列管理器
        
        Args:
            max_workers: 最大工作线程数，对于语音服务器应该设为1以确保同步
        """
        self.max_workers = max_workers
        self.task_queue = queue.PriorityQueue()
        self.workers = []
        self.running = False
        self.lock = threading.Lock()
        self.current_task = None
        
        # 统计信息
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        
        self.logger.info(f"请求队列管理器初始化 | 最大工作线程: {max_workers}")
    
    def start(self):
        """启动队列处理"""
        with self.lock:
            if self.running:
                return
            
            self.running = True
            
            # 创建工作线程
            for i in range(self.max_workers):
                worker = threading.Thread(
                    target=self._worker,
                    name=f"QueueWorker-{i+1}",
                    daemon=True
                )
                worker.start()
                self.workers.append(worker)
            
            self.logger.info(f"队列管理器已启动 | 工作线程数: {len(self.workers)}")
    
    def stop(self):
        """停止队列处理"""
        with self.lock:
            if not self.running:
                return
            
            self.running = False
            
            # 向队列添加停止信号
            for _ in range(self.max_workers):
                self.task_queue.put((0, time.time(), None))
        
        # 等待所有工作线程结束
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        self.workers.clear()
        self.logger.info("队列管理器已停止")
    
    def submit_task(self, 
                   task_id: str,
                   func: Callable,
                   args: tuple = (),
                   kwargs: dict = None,
                   callback: Optional[Callable] = None,
                   priority: int = 0) -> bool:
        """
        提交任务到队列
        
        Args:
            task_id: 任务ID
            func: 要执行的函数
            args: 函数参数
            kwargs: 函数关键字参数
            callback: 完成回调函数
            priority: 优先级（数字越小优先级越高）
        
        Returns:
            bool: 是否成功提交
        """
        if not self.running:
            self.start()
        
        if kwargs is None:
            kwargs = {}
        
        task = QueueTask(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            callback=callback,
            priority=priority
        )
        
        # 使用优先级队列，优先级相同时按提交时间排序
        queue_item = (priority, time.time(), task)
        
        try:
            self.task_queue.put(queue_item, timeout=1.0)
            self.total_tasks += 1
            
            queue_size = self.task_queue.qsize()
            self.logger.info(f"任务已提交到队列 | ID: {task_id} | 队列长度: {queue_size}")
            
            return True
        except queue.Full:
            self.logger.error(f"队列已满，任务提交失败 | ID: {task_id}")
            return False
    
    def _worker(self):
        """工作线程主循环"""
        thread_name = threading.current_thread().name
        self.logger.info(f"工作线程启动: {thread_name}")
        
        while self.running:
            try:
                # 获取任务，超时1秒
                queue_item = self.task_queue.get(timeout=1.0)
                priority, submit_time, task = queue_item
                
                # 检查停止信号
                if task is None:
                    break
                
                self.current_task = task
                queue_size = self.task_queue.qsize()
                
                self.logger.info(f"开始处理任务 | ID: {task.task_id} | 剩余队列: {queue_size}")
                
                start_time = time.time()
                result = None
                error = None
                
                try:
                    # 执行任务
                    result = task.func(*task.args, **task.kwargs)
                    self.completed_tasks += 1
                    
                    elapsed = time.time() - start_time
                    self.logger.info(f"任务完成 | ID: {task.task_id} | 耗时: {elapsed:.2f}s")
                    
                except Exception as e:
                    error = e
                    self.failed_tasks += 1
                    self.logger.error(f"任务执行失败 | ID: {task.task_id} | 错误: {str(e)}")
                
                finally:
                    self.current_task = None
                    
                    # 调用回调函数
                    if task.callback:
                        try:
                            task.callback(task.task_id, result, error)
                        except Exception as e:
                            self.logger.error(f"回调函数执行失败 | ID: {task.task_id} | 错误: {str(e)}")
                    
                    # 标记任务完成
                    self.task_queue.task_done()
                
            except queue.Empty:
                # 超时，继续循环
                continue
            except Exception as e:
                self.logger.error(f"工作线程异常: {str(e)}")
        
        self.logger.info(f"工作线程结束: {thread_name}")
    
    def get_status(self) -> dict:
        """获取队列状态"""
        return {
            "running": self.running,
            "queue_size": self.task_queue.qsize(),
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "current_task": self.current_task.task_id if self.current_task else None,
            "workers": len(self.workers)
        }
    
    def wait_for_completion(self, timeout: Optional[float] = None):
        """等待所有任务完成"""
        self.task_queue.join()
        self.logger.info("所有任务已完成")


# 全局队列管理器实例
_queue_manager = None


def get_queue_manager() -> RequestQueueManager:
    """获取全局队列管理器实例"""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = RequestQueueManager(max_workers=1)  # 语音服务器只能同步处理
    return _queue_manager


def shutdown_queue_manager():
    """关闭全局队列管理器"""
    global _queue_manager
    if _queue_manager:
        _queue_manager.stop()
        _queue_manager = None
