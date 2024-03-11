"use strict";

function randomColor() {
    var color = "#";
    for (var i = 0; i < 3; i++) {
        color += Math.floor(Math.random() * 256).toString(16);
    }
    return color;
}

class Showcase {
    constructor(elementId, items) {
        this.canvas = document.getElementById(elementId);
        this.ctx = this.canvas.getContext("2d");
        this.data = [];

        this.build(document.querySelectorAll(items));
        this.resize();
        this.draw();

        window.addEventListener("resize", () => this.resize());
    }

    resize() {
        var ratio = window.devicePixelRatio || 1;
        this.canvas.width = this.canvas.offsetWidth * ratio;
        this.canvas.height = this.canvas.offsetHeight * ratio;
        this.ctx.scale(ratio, ratio);
        this.ctx.font = "bold 20px Arial";
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        for (var i = 0; i < this.data.length; i++) {
            var item = this.data[i];
            this.ctx.fillStyle = item.color;
            this.ctx.fillText(item.text, item.x, item.y);
            item.x += item.speed;
            if (item.x > this.canvas.offsetWidth) {
                this.arrange(item);
            }
        }
        requestAnimationFrame(() => this.draw());
    }

    build(elements) {
        var texts = [];
        for (var i = 0; i < elements.length; i++) {
            texts.push(elements[i].textContent);
        }
        this.data = [];
        for (var i = 0; i < texts.length; i++) {
            this.data.push({
                text: texts[i],
                x: Math.random() * this.canvas.offsetWidth,
                y: Math.random() * (this.canvas.height - 20),
                color: randomColor(),
                speed: Math.random() * 5 + 1
            });
        }
    }

    arrange(item) {
        item.x = -300;
        item.y = Math.random() * (this.canvas.height - 20);
        item.color = randomColor();
        item.speed = Math.random() * 5 + 1;
    }
}

var showcase = new Showcase("showcase", "#showcase li");
