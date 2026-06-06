---
hide:
  - navigation
  - toc
---

# 友链

<style>
.links-div li > p:nth-child(1) {
    position: relative;
}
.links-div li > p:nth-child(1) > img {
    height: 100%;
    position: absolute;
    float: right;
    right: 0;
    border-radius: 2px;
}
.links-div li > p:nth-child(4) > a > span:nth-child(1) {
    margin-top: .2%;
}
</style>

<div class="links-div grid cards" markdown>

-   __饼藏情敌的博客__ ![avatar](https://q.qlogo.cn/g?b=qq&nk=822627809&s=640)

    ---

    在追求梦想的路上，坚持不懈

    [:octicons-arrow-right-24: 过去看看](https://zjhzzy.github.io)

-   __洛元の小屋__ ![avatar](https://blog.dimeta.top/upload/avatar.jpg)

    ---

    洛元の小屋，科技、游戏、生活为主的 blog

    [:octicons-arrow-right-24: 过去看看](https://blog.dimeta.top)

-   __Adpro の Blog__ ![avatar](https://blog.adproqwq.top/avatar.png)

    ---

    Adpro 的 Blog，可能有有用的东西？

    [:octicons-arrow-right-24: 过去看看](https://blog.adproqwq.top)

-   __Coolloong's Blog__ ![avatar](https://avatars.githubusercontent.com/u/69153398?v=4)

    ---

    Coolloong 的博客

    [:octicons-arrow-right-24: 过去看看](https://coolloong.github.io)

-   __Young's Toy Box__ ![avatar](https://avatars.githubusercontent.com/u/25684570?v=4)

    ---

    玩具盒

    [:octicons-arrow-right-24: 过去看看](https://wesley-young.github.io)

> 期待你的加入 ~

</div>

<script>
    const ul = document.querySelector('.links-div ul');
    const lis = Array.from(ul.children);

    for (let i = lis.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [lis[i], lis[j]] = [lis[j], lis[i]];
    }

    ul.innerHTML = '';
    lis.forEach(li => ul.appendChild(li));
</script>
