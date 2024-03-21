"use strict";

// Return a random color
function randomColor() {
    var color = "#";
    for (var i = 0; i < 3; i++) {
        color += Math.floor(Math.random() * 256).toString(16);
    }
    return color;
}

// Return a random element from an array
function random(array) {
    var index = Math.floor(Math.random() * array.length);
    return array[index];
}

// Change the splash text
var splash = ["Don't touch my gun!", "Medic!", "Help!", "Push the cart!", "I need some doggone help!"];
document.getElementById("shaker").textContent = random(splash);

// Shaker class
class Shaker {
    constructor(elementId) {
        // Get the original element and create a new div
        this.original = document.getElementById(elementId);
        this.div = document.createElement("div");

        // Set the speed and range
        this.speed = 30;
        this.range = 4;

        // Build and shake the text
        this.build();
        this.shake();
    }

    // Build the text
    build() {
        var character;
        for (var i = 0; i < this.original.textContent.length; i++) {
            character = document.createElement("span");
            character.textContent = this.original.textContent[i];
            this.div.appendChild(character);
        }
        this.original.textContent = "";
        this.original.appendChild(this.div);
    }

    // Shake the text
    shake() {
        var characters = this.div.children;
        for (var i = 0; i < characters.length; i++) {
            characters[i].style.position = "relative";
            characters[i].style.left = Math.random() * this.range - this.range / 2 + "px";
            characters[i].style.top = Math.random() * this.range - this.range / 2 + "px";
        }
        setTimeout(() => this.shake(), this.speed);
    }
}

// Create a new shaker
var shaker = new Shaker("shaker");

// Showcase class
class Showcase {
    constructor(elementId, items) {
        // Get the canvas and context
        this.canvas = document.getElementById(elementId);
        this.ctx = this.canvas.getContext("2d");
        this.data = [];

        // Build, resize and draw the text
        this.build(document.querySelectorAll(items));
        this.resize();
        this.draw();

        // Resize the canvas when the window is resized
        window.addEventListener("resize", () => this.resize());
    }

    // Resize the canvas
    resize() {
        var ratio = window.devicePixelRatio || 1;
        this.canvas.width = this.canvas.offsetWidth * ratio;
        this.canvas.height = this.canvas.offsetHeight * ratio;
        this.ctx.scale(ratio, ratio);
        this.ctx.font = "bold 20px Arial";
    }

    // Draw the text
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

    // Build the text
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

    // Arrange the text
    arrange(item) {
        item.x = -300;
        item.y = Math.random() * (this.canvas.height - 20);
        item.color = randomColor();
        item.speed = Math.random() * 5 + 1;
    }
}

// Create a new showcase
var showcase = new Showcase("showcase", "#showcase li");
