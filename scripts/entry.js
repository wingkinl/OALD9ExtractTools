// modified version based on original author: zzzz_sleep from pdawiki.com
function makeActiveFunction()
{
    return function (e) {
        this.parentElement.classList.toggle("is-active");
        e.preventDefault();
    }
}
var all = document.querySelectorAll('.unbox > .heading')
for (i in all) {
    var item = all[i]
    var func = makeActiveFunction();
    item.onclick = func;
}