import axios from 'axios';
export const requestLogin = params => {
  return axios.post(`/api/login`, params).then(res => res.data);
};

export const getTodoList = params => {
  return axios.get(`/api/todo/list`, {
    params: params
  });
};

export const getTodo = params => {
  return axios.get(`/api/todo/listId`, {
    params: params
  });
};

export const addRecord = params => {
  return axios.post(`/api/todo/addRecord`, params).then(res => res.data);
};

export const editTodo = params => {
  return axios.post(`/api/todo/editTodo`, params).then(res => res.data);
};
export const editRecord = params => {
  return axios.post(`/api/todo/editRecord`, params).then(res => res.data);
};

export const addTodo = params => {
  return axios.post(`/api/todo/addTodo`, params).then(res => res.data);
};

// export const editUser = params => { return axios.get(`${base}/user/edit`, { params: params }); };

// export const addUser = params => { return axios.get(`${base}/user/add`, { params: params }); };
