/*https://baejino.com/programing/django/how-to-make-pagination-and-infinite-scroll*/
class InfiniteScroll {
    constructor (path, wrapperId, rastPage) {
        if (path === undefined || wrapperId === undefined) throw Error ('no parameter.');
        this.path = path;
        this.pNum = 2;
        this.wNode = document.getElementById(wrapperId);
        this.wrapperId = wrapperId;
        this.rastPage = rastPage;
        this.enable = true;
        
        this.detectScroll();
    }

    detectScroll() {
        //window -> ul scroll감지로 변경
        var scroll = document.getElementById('scroll');
        var self = this;
        $("#scroll").scroll(function() {
            if (scroll.scrollTop + 800 >= scroll.scrollHeight)
                $(function () {
                self.getNewPost();
                })
        });
    }
    getNewPost() {
        if (this.enable === false) return false;
        this.enable = false;
        const xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = () => {
            if (xmlhttp.readyState == XMLHttpRequest.DONE) {
                if (xmlhttp.status == 200 && this.pNum <= this.rastPage) {
                    this.pNum++;
                    const childItems = this.getChildItemsByAjaxHTML(xmlhttp.responseText);
                    this.appendNewItems(childItems);
                }
                return this.enable = true;
            }
        }
        xmlhttp.open("GET", `${location.origin + this.path + this.pNum}`, true);
        document.getElementById("page").value = this.pNum;
        xmlhttp.send();
    }

    getChildItemsByAjaxHTML(HTMLText) {
        const newHTML = document.createElement('html');
        newHTML.innerHTML = HTMLText;
        const childItems = newHTML.querySelectorAll(`#${this.wrapperId} > *`);
        return childItems;
    }

    appendNewItems(items) {
        items.forEach(item => {
            this.wNode.appendChild(item);
        });
    }
}