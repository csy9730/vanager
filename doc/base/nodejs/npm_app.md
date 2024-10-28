# npm app

## npm about

```bash
npm install -g cnpm --registry=https://registry.npmmirror.com # https://registry.npm.taobao.org
```

## start mode

### 前后分离

- 前端服务器 nodejs 提供的 vue-cli-service , 实际调用  `vue-cli-service serve`，提供 html 服务。
- 后端服务器 python 提供的 flask，提供 api 服务。


#### 前后暴露

前后端都暴露给用户，所以跨域问题是避免不了的

#### 前端暴露

似乎没法不暴露后端服务器。

#### 后端暴露

- 前端打包成 html 
- 后端提供 html 分发 和 api 服务

release 一般使用这种模式。


### router.mode

路由是由多个URL组成的，使用不同的URL可以相应的导航到不同的位置。

如果有进行过服务器开发或者对http协议有所了解就会知道，浏览器中对页面的访问是无状态的，所以我们在切换不同的页面时都会重新进行请求。而实际使用vue和vue-router开发就会明白，在切换页面时是没有重新进行请求的，使用起来就好像页面是有状态的，这是什么原因呢。

这其实是借助了浏览器的History API来实现的，这样可以使得页面跳转而不刷新，页面的状态就被维持在浏览器中了。

vue-router中默认使用的是hash模式，也就是会出现如下的URL：，URL中带有#号

Vue 前端路由使用 hash 模式，是因为 hash 模式不需要后端支持，而且可以在不改变 URL 的同时实现页面跳转和数据更新。


- Hash: 使用URL的hash值来作为路由。支持所有浏览器。
- History: 以来HTML5 History API 和服务器配置。参考官网中HTML5 History模式
- Abstract： 支持所有javascript运行模式。如果发现没有浏览器的API，路由会自动强制进入这个模式。



### production & debug


在Vue.js中，有两种常见的构建Web页面的模式：

开发模式（Development Mode）： 在开发模式下，Vue.js提供了丰富的开发工具和调试功能，方便开发者进行快速的前端开发和调试。在开发模式下，Vue.js会输出有关错误信息和警告的详细日志，帮助开发者定位问题和调试代码。开发模式下的构建文件通常较大，包含了额外的调试代码和开发工具。

生产模式（Production Mode）： 在生产模式下，Vue.js会对代码进行优化和压缩，去除调试和开发工具，以提高页面加载速度和性能。生产模式下的构建文件通常较小，适合在实际生产环境中使用。

在Vue.js中，开发者可以通过设置环境变量（例如通过Vue CLI中的process.env.NODE_ENV）来切换开发模式和生产模式。在开发阶段，开发者通常使用开发模式进行前端开发和调试，而在将网站或应用程序部署到生产环境时，则使用生产模式构建和发布。

开发者可以在项目根目录下的package.json文件中配置构建脚本，以指定不同的构建模式。例如，在Vue CLI项目中，可以通过npm run serve启动开发服务器（开发模式），通过npm run build进行生产模式构建


`process.env.NODE_ENV !== 'production'`
### mock & no mock



## mode design

- vue + mock
- vue + nomock + flask app
- vue/dist + flask app