# vuex

### MVVM
MVC 架构

M 对应数据模型， V 对应界面， C 对应两者的控制，M对V的绑定关系。 点击按键，修改M，修改视图。

MVVM 架构，M 对应数据模型， V 对应界面， VM 对应两者的中间段。

相当于 全局变量，维护 M 和 V 关系的状态。必须通过 vuex store 的访问函数 去访问 全局状态，不能直接访问变量，这会导致状态不一致。

#### 访问机制
提供了多种访问机制：
direct 
getter  计算得到衍生变量
mutation
action

#### mutation
你不能直接调用一个 mutation 处理函数
store.commit('increment') mutation

 mutation 必须是同步函数。
 
#### Action
 Action 类似于 mutation，不同在于：

Action 提交的是 mutation，而不是直接变更状态。
Action 可以包含任意异步操作。

Action 通过 store.dispatch 方法触发：