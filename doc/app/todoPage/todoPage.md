#### todo.model

- Todolist todo项目
- TodoRecord todo子项

Todolist 对应多个 TodoRecord


#### todo.vue 

- TodoView.vue
	- TodoMenus   Todolist列表
	- router-view
		- TodoItem.vue  单个Todolist
			- TodoRec.vue 单个TodoRecord
			
	
```		
TodoView.vue{
<TodoMenus></TodoMenus>
router-view { '/todo/:id': 'TodoItem.vue'}
}
```

