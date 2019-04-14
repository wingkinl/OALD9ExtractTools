// original author: zzzz_sleep from pdawiki.com
function makeActiveFunction()
{
    return function (e) {
        this.classList.toggle("is-active");
        e.preventDefault();
    }
}
var all = document.getElementsByClassName("unbox")
for (i in all) {
    var item = all[i]
    var func = makeActiveFunction();
    item.onclick = func;
}