import time
import uuid
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

# ====================== 1. 系统枚举与数据结构 ======================
class AgentType(Enum):
    COORDINATOR = "中央协调Agent"
    DATA_AGENT = "数据采集Agent"
    CONTENT_AGENT = "内容生成Agent"
    EXECUTE_AGENT = "执行运营Agent"

class TaskStatus(Enum):
    PENDING = "待执行"
    RUNNING = "执行中"
    SUCCESS = "执行成功"
    FAILED = "执行失败"

@dataclass
class Task:
    task_id: str
    content: str
    agent_type: AgentType
    depend_on: Optional[str] = None  # 依赖任务ID
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    error: str = ""

@dataclass
class Agent:
    agent_id: str
    agent_type: AgentType
    name: str
    is_busy: bool = False

# ====================== 2. 基础智能体（运营专用） ======================
class BaseAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.log(f"已启动 → {self.agent.name}")

    def log(self, msg: str):
        print(f"[{self.agent.name}] {msg}")

    def execute(self, task: Task) -> bool:
        pass

# 数据Agent：负责报表、指标、数据拉取
class DataAgent(BaseAgent):
    def execute(self, task: Task) -> bool:
        try:
            self.log(f"开始处理任务：{task.content}")
            time.sleep(1)  # 模拟执行耗时
            task.result = "✅ 数据采集完成：昨日UV=12800，转化率=4.2%，GMV=86500元"
            task.status = TaskStatus.SUCCESS
            self.log("任务执行成功")
            return True
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.log(f"任务失败：{str(e)}")
            return False

# 内容Agent：负责文案、海报、推送内容生成
class ContentAgent(BaseAgent):
    def execute(self, task: Task) -> bool:
        try:
            self.log(f"开始处理任务：{task.content}")
            time.sleep(1)
            task.result = "✅ 内容生成完成：运营推送文案+3张活动海报已就绪"
            task.status = TaskStatus.SUCCESS
            self.log("任务执行成功")
            return True
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            return False

# 执行Agent：负责自动发布、消息推送、自动化操作
class ExecuteAgent(BaseAgent):
    def execute(self, task: Task) -> bool:
        try:
            self.log(f"开始处理任务：{task.content}")
            time.sleep(1)
            task.result = "✅ 执行完成：活动已自动上线，用户群推送完成"
            task.status = TaskStatus.SUCCESS
            self.log("任务执行成功")
            return True
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            return False

# ====================== 3. 中央协调器（核心大脑） ======================
class CoordinatorAgent(BaseAgent):
    def __init__(self, agent: Agent):
        super().__init__(agent)
        self.agent_pool: Dict[AgentType, BaseAgent] = {}
        self.task_queue: List[Task] = []
        self.task_map: Dict[str, Task] = {}

    # 注册智能体
    def register_agent(self, agent: BaseAgent):
        self.agent_pool[agent.agent.agent_type] = agent
        self.log(f"已注册 → {agent.agent.name}")

    # 添加任务
    def add_task(self, task: Task):
        self.task_queue.append(task)
        self.task_map[task.task_id] = task

    # 检查任务依赖是否完成
    def is_depend_done(self, task: Task) -> bool:
        if not task.depend_on:
            return True
        depend_task = self.task_map.get(task.depend_on)
        return depend_task and depend_task.status == TaskStatus.SUCCESS

    # 执行单任务
    def run_single_task(self, task: Task):
        if task.status != TaskStatus.PENDING:
            return
        if not self.is_depend_done(task):
            return

        agent = self.agent_pool.get(task.agent_type)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = "无可用执行Agent"
            return

        task.status = TaskStatus.RUNNING
        agent.execute(task)

    # 任务调度总入口
    def run_all_task(self):
        self.log("===== 开始执行多Agent协同运营自动化任务 =====")
        total = len(self.task_queue)
        success = 0

        while True:
            unfinished = [t for t in self.task_queue if t.status in [TaskStatus.PENDING, TaskStatus.RUNNING]]
            if not unfinished:
                break

            for task in self.task_queue:
                self.run_single_task(task)

            time.sleep(0.5)

        # 统计结果
        for t in self.task_queue:
            if t.status == TaskStatus.SUCCESS:
                success += 1

        self.log(f"\n===== 任务执行完成 | 总数={total} | 成功={success} =====")

    # 输出最终报告
    def generate_final_report(self):
        self.log("\n===== 多Agent协同运营最终报告 =====")
        for task in self.task_queue:
            print(f"\n【任务】{task.content}")
            print(f"状态：{task.status.value}")
            print(f"结果：{task.result if task.result else task.error}")
        print("="*60)

# ====================== 4. 系统启动入口（演示流程） ======================
if __name__ == "__main__":
    # 1. 创建中央协调器
    coordinator = CoordinatorAgent(
        Agent(
            agent_id=str(uuid.uuid4()),
            agent_type=AgentType.COORDINATOR,
            name="中央运营协调器"
        )
    )

    # 2. 创建并注册3大运营Agent
    coordinator.register_agent(DataAgent(Agent(uuid.uuid4().__str__(), AgentType.DATA_AGENT, "数据采集Agent")))
    coordinator.register_agent(ContentAgent(Agent(uuid.uuid4().__str__(), AgentType.CONTENT_AGENT, "内容生成Agent")))
    coordinator.register_agent(ExecuteAgent(Agent(uuid.uuid4().__str__(), AgentType.EXECUTE_AGENT, "自动执行Agent")))

    # 3. 创建运营任务（带依赖：数据→内容→执行）
    t1 = Task(uuid.uuid4().__str__(), "采集昨日运营数据", AgentType.DATA_AGENT)
    t2 = Task(uuid.uuid4().__str__(), "根据数据生成活动内容", AgentType.CONTENT_AGENT, depend_on=t1.task_id)
    t3 = Task(uuid.uuid4().__str__(), "自动上线活动并推送用户", AgentType.EXECUTE_AGENT, depend_on=t2.task_id)

    # 4. 加入任务队列
    coordinator.add_task(t1)
    coordinator.add_task(t2)
    coordinator.add_task(t3)

    # 5. 启动协同执行
    coordinator.run_all_task()

    # 6. 输出最终运营报告
    coordinator.generate_final_report()