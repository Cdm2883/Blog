---
date: 2025-08-24
categories:
  - 技术
tags:
  - Reversing
  - Node.js
---

# 逆向分析：揭秘某国产知名视频弹幕网站客户端暗藏的可爱小桌宠

当你沉浸在刷视频的快乐时，或许从未想过：你电脑里的软件，可能还藏着开发者悄悄埋下的**小惊喜**。
最近，我在一次逆向分析中，意外发现某国产知名视频弹幕网站的 PC 客户端中，
竟然暗藏着一个可以互动、还能换装的 Live2D 小桌宠！
别急，这篇文章将带领你逐步拆解应用，层层剥开这神秘“外衣”下的秘密。

<!-- more -->

## 事情的起因

那天晚上，我的一位朋友在我群里发来了一张这样的截图：

<!--suppress CssUnusedSymbol -->
<style>
    .friend-message {
        border-radius: 6px;
    }
</style>
![朋友的消息](../assets/images/electron-app-devmode-analysis/friend_message_light.png#only-light){ .friend-message }
![朋友的消息](../assets/images/electron-app-devmode-analysis/firend_message_dark.png#only-dark){ .friend-message }

通过连续多次点击 **关于 XXXX** 这个小标题，能够打开一个“开发者模式”的弹窗，看样子还需要一个**密码**才能开启。
这一下就勾起了我的好奇心。问题是，怎样才能知道这个密码呢？

## 开始分析

!!! warning "免责声明"

    本文所涉及的技术、工具及示例仅用于学习和研究目的，不得将上述内容用于商业或者非法用途，
    否则，一切因不当使用本文信息而造成的任何后果由使用者自行承担！

首先我们进入软件安装目录，很容易就能确认，这是一个用 [Electron](https://electronjs.org/zh) 制作的应用。
Electron 是 Node.js + Chromium 混合的产物，同样也能接收 `--inspect` 等命令行参数用于打开调试器端口。

于是，我们打开终端，尝试带上调试参数启动应用，结果发现：
它竟然没有屏蔽这个参数！这意味着，我们的分析就会变得容易许多了。

既然弹窗是在前端显示的，那么理论上，我们可以通过为渲染进程启用远程调试端口（`--remote-debugging-port`），
并用我们的浏览器进行连接（`chrome://inspect`）来实现类似正常浏览器 "++f12++" (DevTools) 的功能。  
然而，实际操作后却发现：虽然浏览器连上了端口，但界面无法正常调试！

## 为渲染进程启用 DevTools

那该如何是好？是时候使用辣个东西了 —— [`chii`](https://github.com/liriliri/chii)！
这是一个远程调试工具，其在 JS 层实现了 Chrome DevTools Protocol，用来提供有限的 DevTools 界面和功能。
使用只需要简单地向页面注入一个 `#!html <script>` 标签。

鉴于主进程的 `--inspect` 是能够正常使用的，我们可以在主进程拿到 `BrowserWindow`，
并利用 `#!js BrowserWindow.webContents.executeJavaScript(...)` 来往页面添加 script 标签。

为了后续调试方便，这里我使用 Node.js 写了一个简单的启动应用并注入 JS 的小脚本，
这样每次重启应用就不用手动在 `chrome://inspect` 操作了。

```json title="package.json"
{
  "main": "inject/main.js",
  "scripts": {
    "start": "node start.js"
  },
  "dependencies": {
    "chii": "^1.15.5",
    "node-fetch": "^3.3.2",
    "ps-list": "^8.1.1",
    "ws": "^8.18.3"
  },
  "devDependencies": {
    "@types/node": "16.18.0",
    "@types/ws": "^8.18.1",
    "electron": "21.3.3"
  }
}
```

```js title="start.js" linenums="1"
const { sep } = require("node:path");
const { spawn } = require("node:child_process");
const WebSocket = require("ws");

const executablePath = "D:\\Program Files\\????????";  // 软件所在目录
const executableName = "????.exe";  // 软件可执行文件的名称
const nodeInspectorPort = 9229;
// const chromeInspectorPort = 9222;

(async () => {
    const { default: psList } = require('ps-list');
    const processes = await psList();
    processes.filter(p => p.name === executableName)
        .forEach(p => process.kill(p.pid, 'SIGKILL'));

    const args = [
        '--inspect=' + nodeInspectorPort,
        // '--remote-debugging-port=' + chromeInspectorPort,
    ];
    spawn(
        executablePath + sep + executableName,
        args,
        { stdio: 'inherit' },
    );
    await inject();
})();

/** @returns {Promise<string>} */
const getNodeInspectorUrl = async () => {
    try {
        const response = await fetch(`http://127.0.0.1:${nodeInspectorPort}/json/list`);
        const targets = await response.json();
        return targets[0].webSocketDebuggerUrl;
    } catch (_) {
        return await getNodeInspectorUrl();
    }
};

async function inject() {
    // 连接上 Node.js（主进程）的 Inspector
    const ws = new WebSocket(await getNodeInspectorUrl());
    let id = 0;
    const call = (method, params) => ws.send(JSON.stringify({
        id: ++id, method, params,
    }));
    ws.on('open', () => {
        call('Debugger.enable');
        // 然后在指定文件开头下个断点 (1)
        call('Debugger.setBreakpointByUrl', {
            lineNumber: 0,
            // 软件加载到这里的时候，所有窗口就已经创建好了
            urlRegex: 'file:///.+/@.+/keep-pc-alive/index.js',
        });
    });
    ws.on('message', raw => {
        const data = JSON.parse(raw.toString())
        const { method, params } = data;
        console.log(data);
        if (method !== 'Debugger.paused') return;
        // 在断点处执行代码
        call('Debugger.evaluateOnCallFrame', {
            callFrameId: params.callFrames[0].callFrameId,
            // 这里使用 __dirname 最终会运行刚刚我们在 package.json 中设置的 main 字段
            expression: 'require(String.raw`' + __dirname + '`)',
            returnByValue: true,
        });
        call('Debugger.resume');  // 恢复代码的执行
        ws.close();
    });
}
```

1. 关于为什么要断点后再在断点处执行代码，
   而不是直接用 [`Runtime.evaluate`](https://chromedevtools.github.io/devtools-protocol/tot/Runtime/#method-evaluate)。  
   一是在最开始的时候，Node.js 环境还没有准备好，这会在裸的 V8 环境上运行代码，也就没有 `require` 方法的存在。  
   二是 `Runtime.evaluate` 需要提供 `contextId` 或 `uniqueContextId`，不然你还是在 V8 裸环境中运行；
   而这样我们还需要确认我们使用的 ID 是属于哪个环境，否则依然无法拿到正确的 `process` 或 `require`。

```js title="inject/main.js"
const net = require("node:net");
const chii = require("chii");
// 这个软件的 Node.js 版本有点老，`global` 上没有 `fetch` XD
const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));
const { BrowserWindow } = require('electron');

const port = (() => {
    const server = net.createServer().listen(0);
    const { port } = server.address();
    return server.close() && port;
})();
chii.start({ port }).then();

async function createDevtoolsWindow(window) {
    const url = window.webContents.getURL().split('#')[0];
    const targets = await fetch(`http://localhost:${port}/targets`);
    const target = (await targets.json()).targets
        .reverse()
        .find(it => it.url.split('#')[0] === url);
    const devtools = new BrowserWindow({ autoHideMenuBar: true });
    devtools.loadURL(`http://localhost:${port}/front_end/chii_app.html`
        + `?ws=localhost:${port}/client/Cdm2883?target=${target.id}`)
        .then();
    return devtools;
}

BrowserWindow.getAllWindows().forEach(window => {
    let devtoolsWindow = undefined;
    const switchWindow = () => devtoolsWindow === undefined ?
        createDevtoolsWindow(window).then(it =>
            devtoolsWindow = it.on('close', () => devtoolsWindow = undefined))
        : devtoolsWindow = void devtoolsWindow.close();
    window.webContents.on('before-input-event', (_event, input) =>
        input.key === 'F12' && input.type === 'keyDown' && switchWindow());
    window.webContents.executeJavaScript(`
        var script = document.createElement('script');
        script.src = 'http://localhost:${port}/target.js';
        document.head.append(script);`).then();
});
```

---

现在一切准备就绪！我们在终端运行 `npm run start`。
等待软件加载完毕，我们再按下 ++f12++，DevTool 就以新窗口的形式出现了！
{>>虽然好像因为 Chromium 版本太旧了导致图标显示都不正常，但是还是可以按照肌肉记忆来操作 XD<<}

## 分析前端逻辑

接下来我们来到 `Sources` 面板，发现里面的 JS 都是混淆过的。
其中的非 ASCII 字符串都被编码为了 Unicode 转义序列。
经过一番简单的观察，会发现应用使用了 Vue.js 进行开发，所以我们可以尝试在 JS 中定位到生成“开发者模式”弹窗的代码。

试试搜索这附近的其他文本？比如：`#!js "反馈意见"`。
同时搜索这段非 ASCII 字符串的时候也需要编码一下，我们可以简单地随便找个 JS 环境运行一下这段代码：

```js
const unicode = '反馈意见'
    .split('')
    .map(c => '\\u' + c.charCodeAt(0)
        .toString(16)
        .toUpperCase()
        .padStart(4, '0'))
    .join('');
console.log(unicode);  // \u53CD\u9988\u610F\u89C1
```

接下来我们在 `./assets` 目录下的 JS 文件中都尝试使用 ++ctrl+f++ 搜索这段字符，
很快就能找到这些代码属于文件 `./assets/index.e4a93139.js`

然后我们把内容都复制出来，使用 [de4js](https://lelinhtinh.github.io/de4js)
这个在线工具进行反混淆以方便我们的阅读。  
去除掉无关部分，内联部分代码，最终得到：

```js title="index.e4a93139.js (part)" linenums="1" hl_lines="8-16 84"
const _sfc_main$6 = defineComponent({
  __name: "About????????",
  setup(a) {
    const o = ref(!1),
      s = ref("") /* ... */ ;
    // ...
    const /* ... */
      _ = () => {
        o.value = !1, m(!0, s.value)
      },
      f = $ => {
        $.key === "Enter" && _()
      },
      m = ($, g = "") => {
        callNative$1("config/setIsDevMode", $, g)
      } /* ... */ ;
    return ($, g) => {
      const B = resolveComponent("v-button"),
        C = resolveComponent("v-dialog");
      return openBlock(),
        createElementBlock(Fragment, null, [
          createBaseVNode("div", { /* ... */ }, [
            createBaseVNode("h4", { /* ... */ }, "关于????"),
            createBaseVNode("div", { /* ... */ }, [
              createBaseVNode("span", { /* ... */ }, [
                createTextVNode(" 当前版本："),
                createBaseVNode("span", { /* ... */ },
                  toDisplayString(unref(l))
                    + toDisplayString(unref(IS_DEV_MODE) ? " (开发者模式)" : "")
                , 1)
              ])
            ]),
            createBaseVNode("div", { /* ... */ }, [
              unref(IS_DEV_MODE) && unref(IS_RELEASE)
                ? (openBlock(), createBlock(B, {
                  // ...
                  onClick: g[0] || (g[0] = b => m(!1))
                }, {
                  default: withCtx(() => [
                    createVNode(unref(ExitIcon), { /* ... */ }),
                    createTextVNode(" 退出开发模式 ")
                  ]),
                  _: 1
                }))
                : createCommentVNode("", !0),
              createVNode(B, { /* ... */ }, {
                default: withCtx(() => [createTextVNode("检查更新")]),
                _: 1
              }),
              createVNode(B, { /* ... */ }, {
                default: withCtx(() => [createTextVNode("反馈意见")]),
                _: 1
              }),
              createVNode(B, { /* ... */ }, {
                default: withCtx(() => [createTextVNode("客服中心")]),
                _: 1
              })
            ]),
            createBaseVNode("div", { /* ... */ }, [
              createBaseVNode("a", { /* ... */ }, "《????官网》"),
              createBaseVNode("a", { /* ... */ }, "《用户协议》"),
              createBaseVNode("a", { /* ... */ }, "《隐私政策》"),
              unref(c)
                ? (openBlock(), createElementBlock("a", { /* ... */ }, "《开源软件许可》"))
                : createCommentVNode("", !0)
            ])
          ]),
          createVNode(C, {
            visible: o.value,
            "onUpdate:visible": g[8] || (g[8] = b => o.value = b),
            title: "开发者模式",
            "mask-closable": !1,
            onOk: _,
            onCancel: g[9] || (g[9] = b => o.value = !1)
          }, {
            default: withCtx(() => [
              createBaseVNode("div", { /* ... */ }, [
                createBaseVNode("div", { class: "dev-mode-pwd" }, [
                  createBaseVNode("label", { /* ... */ }, "请输入密码：", -1),
                  withDirectives(createBaseVNode("input", {
                    "onUpdate:modelValue": g[7] || (g[7] = b => s.value = b),
                    type: "password",
                    class: "vuix_input w_100",
                    onKeydown: f
                  }, null, 544), [ [vModelText, s.value] ])
                ])
              ])
            ]),
            _: 1
          }, 8, ["visible"]),
          createVNode(C, { /* ... */ }, {
            default: withCtx(() => [
              createBaseVNode("div", { /* ... */ }, [
                createBaseVNode("h4", { /* ... */ }, "开源软件许可"),
                createBaseVNode("iframe", { /* ... */ })
              ], -1)
            ]),
            _: 1
          }, 8, ["visible"])
        ], 64)
    }
  }
});
```

我们注意到，这个“请输入密码”的输入框响应了一个 `onKeydown` 事件并交给函数 `f` 处理。  
`f` 中当检测到按下的是 ++enter++ 时，会调用函数 `_`。  
最终会调用 `#!js callNative$1("config/setIsDevMode", !0, s.value)`，
其中 `s.value` 与 `input` 绑定，会实时同步输入的内容，也就是我们输入的密码。

通过 `callNative` 这个名称能够猜出，这与主进程有关。所以接下来我们要分析主进程。

## 深入主进程

回到软件安装目录，我们能在 `resources` 目录下找到一个 `app.asar` 文件。
这里通常储存着 Electron 应用的入口以及其他源代码文件。
官方也提供了一个命令行小工具 [`@electron/asar`](https://github.com/electron/asar)，
可以让我们轻松地解压这个文件。

这里面还有一个 `render` 文件夹，里面储存着刚刚我们在 DevTools 看到的文件，吗？
仔细观察，能够惊讶地发现，两者文件数量不一样，而且很多文件内容也对不上！

还记得我们最开始使用的 `start.js` 小脚本吗？
这里的第 58 行我们还输出了一些 DevTools 的调试信息。
观察真实的输出还能发现有许多 [`Debugger.scriptParsed`](https://chromedevtools.github.io/devtools-protocol/tot/Debugger/#event-scriptParsed)
事件被触发，比如：

```js
{
  method: 'Debugger.scriptParsed',
  params: {
    scriptId: '803',
    url: 'file:///C:/Users/Cdm2883/AppData/Roaming/????????/resource/7ea14c4ca3b4ece8.asar/node_modules/express/lib/utils.js',
    startLine: 0,
    startColumn: 0,
    endLine: 303,
    endColumn: 0,
    executionContextId: 1,
    hash: '9035c6d946ece511e749043cc823e32d3efe6727b8a9d52aac89649e99584f09',
    executionContextAuxData: { isDefault: true },
    isLiveEdit: false,
    sourceMapURL: '',
    hasSourceURL: false,
    isModule: false,
    length: 5871,
    stackTrace: { callFrames: [Array] },
    scriptLanguage: 'JavaScript',
    embedderName: 'file:///C:/Users/Cdm2883/AppData/Roaming/????????/resource/7ea14c4ca3b4ece8.asar/node_modules/express/lib/utils.js'
  }
}
```

这里出现了一个未知的 asar 文件，我们对这个文件用同样的方法进行解包，
发现这里的 `render` 文件夹就能够和我们在 DevTools 里看到的对应上了。
所以接下来我们就在这里继续分析。

注意到 `main` 文件夹下有一个 `????-preload.js`，很明显这是在 preload 时期使用的脚本。
然后我们对这个文件使用工具 [JS Deobfuscator](https://js-deobfuscator.vercel.app)
进行反混淆并整理：

```js title="????-preload.js (part)"
var A = require("electron");
A.ipcRenderer.setMaxListeners(1000);
var C = async (f, ...g) => {
   try {
      const i = await A.ipcRenderer.invoke(f, ...g);
      if (i?.hasOwnProperty("error")) {
         return Promise.reject(i.error);
      }
      return i;
   } catch (j) {
      Promise.reject(j);
   }
};
// ...
A.contextBridge.exposeInMainWorld("biliBridgePc", {
   callNative: C,
   // ...
});
```

能够发现这里使用了 ipc 与主进程进行通信。
按理说，会有一个地方使用 `ipcMain` 来响应调用，
但是无论我们在哪个文件夹内搜索都搜索不到包含 ipcMain 的文件；
搜索 `config/setIsDevMode` 也同样无济于事。

根据 `callNative` 这个名称，能够猜到或许这个方法是写在原生代码里面的。
原生代码，无非就在启动的 exe 和关联的动态链接库里或者在 .node 文件里。  
但是我们用 IDA 打开这个 exe 并用 electron 官方提供的 pdb 加载，
发现居然能够加载上，这说明似乎这个 exe 没有被修改过。  
然后要排查 `.node` 文件，可以再次用浏览器打开 `chrome://inspect`，
连接上 Node.js Inspector，最后在控制台运行：

```js
Object.keys(require.cache).filter(s => s.endsWith('.node'))
```

但是输出中没有观察到可疑的文件。
现在连代码在哪个文件都找不到，难道我们的分析就就要停滞在这里了吗？

想一想，既然监听的代码也被加载到了 V8 环境，
那么堆里面一定也能找到 `#!js "config/setIsDevMode"` 这个字符串。
现在我们来到刚刚连接的 DevTools 的“内存”面板，点击获取快照。然后 ++ctrl+f++ 搜索这个字符串：

![堆快照](../assets/images/electron-app-devmode-analysis/memory-heap.png)

发现这个字符串出现在 `global.bootstrapApp` 这个函数内。
如果我们在刚刚的 asar 文件内搜索会发现仅在 `main/index.js` 这个位置调用了这个函数。
但是却找不到这个函数的定义，
这说明也许 `bootstrapApp` 也与 `callNative` 一样在原生代码的某处被定义了。

DevTools 其实有一个查找函数来源的功能。
现在我们在控制台输入 `bootstrapApp` 并回车，然后对着这个函数的值按下 ++ctrl+left-button++。

哇哦，DevTools 将我们带到了一个未知的地方。而且这里还能搜索到我们想要的字符串 `config/setIsDevMode`！
然后我们将这里的代码复制出来，用之前的方法反混淆并整理：

```js
i(
    [
        ag.IpcInvoke("config/setIsDevMode", { scope: "mainWindow" }),
        j("design:type", Function),
        j("design:paramtypes", [Object, Boolean, String]),
        j("design:returntype", Promise)
    ],
    an.prototype,
    "handleSetIsDevMode",
    null
);
```

根据这里能够猜测，当接收到 `config/setIsDevMode` 的调用时，
可能会交给函数 `handleSetIsDevMode` 去处理。意料之中的是，文件内搜索还真能搜到这个函数：

```js
async handleSetIsDevMode(ap, aq, ar) {
    if (!aq || ar === "<秘密>" || ar && ar === '<还是秘密>') {
      this.log.info("Set dev mode: ", aq);
      this.storeService.setIsDev(aq);
      if (aq && ar !== "<秘密>") {
        this.storeService.setTempDevPwd(ar);
      }
      // TOLOOK
      setTimeout(() => this.utilsService.relaunchApp());
    }
}
```

就这样，我们成功地找到了开发者密码！(1)当然为了避免造成不好的影响和不劳而获，我不会直接把密码的明文放在这里。
{ .annotate }

1. 多么有企业文化的密码呀 (゜-゜)つロ

## 开启隐藏小桌宠

回到设置然后输入密码，应用就会重启。然后再次来到设置页面，会发现右上角多了个“显示开发工具”的按钮。
我们点击它，然后开启桌面小助手功能：

![开发设置](../assets/images/electron-app-devmode-analysis/dev-settings-light.png#only-light)
![开发设置](../assets/images/electron-app-devmode-analysis/dev-settings-dark.png#only-dark)

然后重启应用，一只小桌宠就会出现在你的屏幕上了！记得不要去开启窗口调试，不然窗口会有个白底而不是透明底 →_→

## 结语

好了，这就是这篇文章的全部内容啦~ 喜欢的话欢迎在下方留下你的表情回应和评论，对此我表示万分感谢！

本次演示的应用构建号为 `10010170012508131744(20281718)`，你可以滚动到设置页的最下方来查看。
如果和你本机使用的不一致，在跟着文章实际操作时可能会有点出入，但是没关系，大概思路应该是一样的！
快一起来感受逆向所带来的独特乐趣吧！
