var canvas = document.getElementById("paint");
var ctx = canvas.getContext("2d");
var width = canvas.width, height = canvas.height;
var curX, curY, prevX, prevY;
var hold = false;
var isFill = true, isStroke = false, currentTypeColor = 1;

var bounds = canvas.getBoundingClientRect();


window.addEventListener("load", function(){bounds = canvas.getBoundingClientRect();})
window.addEventListener("resize", function(){bounds = canvas.getBoundingClientRect();})
window.addEventListener("scroll", (event) => {
 bounds = canvas.getBoundingClientRect();
})
var pi2 = Math.PI * 2;
var resizerRadius = 8;
var rr = resizerRadius * resizerRadius;

ctx.lineWidth = 2;

var canvas_data = {
  "pencil": [],
  "line": [],
  "rectangle": [],
  "circle": [],
  "eraser": [],
  "last_action": []
};


function color(color_value) {
  if(currentTypeColor == 0){
    ctx.fillStyle = color_value;
  }else{
    ctx.strokeStyle = color_value;
  }
}

function add_pixel() {
  ctx.lineWidth += 1;
}

function reduce_pixel() {
  if (ctx.lineWidth == 1) {
    ctx.lineWidth = 1;
  } else {
    ctx.lineWidth -= 1;
  }
}

function fill() {
  isFill = true;
  if(currentTypeColor == 0){
    isStroke = !isStroke;
  }
  currentTypeColor = 0;
}

function outline() {
   isStroke = true;
  if(currentTypeColor == 1){
    isFill = !isFill;
  }
  currentTypeColor = 1;
}

function reset() {

   if (confirm('Etes vous sûr.e de vouloir effacer le dessin ? ')) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      canvas_data = {
        "pencil": [],
        "line": [],
        "rectangle": [],
        "circle": [],
        "eraser": [],
        "last_action": []
      };
   }
}

// pencil tool
function pencil(data, targetX, targetY, targetWidth, targetHeight) {
    currentTypeColor = 1;
  canvas.onmousedown = function(e) {
    curX = e.clientX - bounds.x;
    curY = e.clientY - bounds.y;
    hold = true;
    ctx.beginPath();
    ctx.moveTo(curX, curY); // prev -> cur;
  };

  canvas.onmousemove = function(e) {
    if (hold) {
          curX = e.clientX - bounds.x;
          curY = e.clientY - bounds.y;
          draw();
          prevX = curX; // new
          prevY = curY; // new
    }
  };

  canvas.onmouseup = function(e) {
    hold = false;
  };

  canvas.onmouseout = function(e) {
    hold = false;
  };

  function draw() {
        ctx.lineTo(curX, curY);
        ctx.stroke();
        if(hold){
            canvas_data.pencil.push({
              "startx": prevX,
              "starty": prevY,
              "endx": curX,
              "endy": curY,
              "thick": ctx.lineWidth,
              "color": ctx.strokeStyle
            });
            canvas_data.last_action.push(0);
        }
  }
}


// line tool
function line (){
    currentTypeColor = 1;

    canvas.onmousedown = function (e){
        img = ctx.getImageData(0, 0, width, height);
        prevX = e.clientX - bounds.x;
        prevY = e.clientY - bounds.y;
        hold = true;
    };

    canvas.onmousemove = function (e){
        if (hold){
            ctx.putImageData(img, 0, 0);
            curX = e.clientX - bounds.x;
            curY = e.clientY - bounds.y;
            ctx.beginPath();
            ctx.moveTo(prevX, prevY);
            ctx.lineTo(curX, curY);
            ctx.stroke();
            ctx.closePath();
        }
    };

    canvas.onmouseup = function (e){
        if (hold){
            canvas_data.line.push({ "startx": prevX, "starty": prevY, "endx": curX, "endy": curY,
                 "thick": ctx.lineWidth, "color": ctx.strokeStyle });
            canvas_data.last_action.push(1);
            }
         hold = false;
    };

    canvas.onmouseout = function (e){
         hold = false;
    };
}

// rectangle tool
function rectangle (){

    canvas.onmousedown = function (e){
        img = ctx.getImageData(0, 0, width, height);
        prevX = e.clientX - bounds.x;
        prevY = e.clientY - bounds.y;
        hold = true;
    };

    canvas.onmousemove = function (e){
        if (hold){
            ctx.putImageData(img, 0, 0);
            curX = e.clientX - bounds.x - prevX;
            curY = e.clientY - bounds.y - prevY;
            if (isStroke){
                ctx.strokeRect(prevX, prevY, curX, curY);
            }
            if (isFill){
                ctx.fillRect(prevX, prevY, curX, curY);
            }

        }
    };

    canvas.onmouseup = function (e){
        if (hold){
            canvas_data.rectangle.push({ "startx": prevX, "starty": prevY, "width": curX, "height": curY,
                "lineWidth": ctx.lineWidth, "isStroke": isStroke, "strokeStyle": ctx.strokeStyle, "isFill": isFill,
                "fillStyle": ctx.fillStyle });
            canvas_data.last_action.push(2);
        }
        hold = false;
    };

    canvas.onmouseout = function (e){
        hold = false;
    };
}

// circle tool

function circle (){
    currentTypeColor = 0;

    canvas.onmousedown = function (e){
        img = ctx.getImageData(0, 0, width, height);
        prevX = e.clientX - bounds.x;
        prevY = e.clientY - bounds.y;
        hold = true;
    };

    canvas.onmousemove = function (e){
        if (hold){
            ctx.putImageData(img, 0, 0);
            curX = e.clientX - bounds.x;
            curY = e.clientY - bounds.y;
            if (prevX != curX && prevY != curY){
                ctx.beginPath();
                ctx.arc(Math.abs(curX + prevX)/2, Math.abs(curY + prevY)/2,
                    Math.sqrt(Math.pow(curX - prevX, 2) + Math.pow(curY - prevY, 2))/2, 0, pi2, true);
                ctx.closePath();
                if (isStroke){
                    ctx.stroke();
                }
                if (isFill){
                    ctx.fill();
                }
            }
        }
    };

    canvas.onmouseup = function (e){
        if (hold){
            curX = e.clientX - bounds.x;
            curY = e.clientY - bounds.y;
            canvas_data.circle.push({ "startx": prevX, "starty": prevY, "endx": curX, "endy": curY, "lineWidth": ctx.lineWidth,
                "isStroke": isStroke, "strokeStyle": ctx.strokeStyle, "isFill": isFill, "fillStyle": ctx.fillStyle });
            canvas_data.last_action.push(3);
        }
        hold = false;
    };

    //canvas.onmouseout = function (e){
    //    hold = false;
    //};
}

// eraser tool

function eraser (){
    canvas.onmousedown = function (e){
        curX = e.clientX - bounds.x;
        curY = e.clientY - bounds.y;
        hold = true;

        prevX = curX;
        prevY = curY;
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
    };

    canvas.onmousemove = function (e){
        if(hold){
            curX = e.clientX - bounds.x;
            curY = e.clientY - bounds.y;
            draw();
        }
    };

    canvas.onmouseup = function (e){
        hold = false;
    };

    canvas.onmouseout = function (e){
        hold = false;
    };

    function draw (){
        ctx.lineTo(curX, curY);
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth =
        ctx.stroke();
        if (prevX != curX && prevY != curY){
            canvas_data.eraser.push({ "startx": prevX, "starty": prevY, "endx": curX, "endy": curY,
                "thick": ctx.lineWidth, "color": ctx.strokeStyle });
            canvas_data.last_action.push(4);
        }

    }
}


function undo_pixel() {

  switch (canvas_data.last_action[canvas_data.last_action.length - 1]) {
    case 0:
      canvas_data.pencil.pop();
      break;
    case 1:
      //Undo the last line drawn
      canvas_data.line.pop();
      break;
    case 2:
      //Undo the last rectangle drawn
      canvas_data.rectangle.pop();
      break;
    case 3:
      //Undo the last circle drawn
      canvas_data.circle.pop();
      break;
    case 3:
      //Undo the last eraser drawn
      canvas_data.eraser.pop();
      break;

    default:
      break;

  }
    redraw_canvas();
    canvas_data.last_action.pop();
}

function redraw_canvas() {
  // Redraw all the shapes on the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  // Redraw the pencil data
  canvas_data.pencil.forEach(function(p) {
    ctx.beginPath();
    ctx.moveTo(p.startx, p.starty);
    ctx.lineTo(p.endx, p.endy);
    ctx.lineWidth = p.thick;
    ctx.strokeStyle = p.color;
    ctx.stroke();
  });
  // Redraw the line data
  canvas_data.line.forEach(function(l) {
    ctx.beginPath();
    ctx.moveTo(l.startx, l.starty);
    ctx.lineTo(l.endx, l.endy);
    ctx.lineWidth = l.thick;
    ctx.strokeStyle = l.color;
    ctx.closePath();
    ctx.stroke();
  });
  canvas_data.rectangle.forEach(function(l) {
        if (l.isStroke){
            ctx.lineWidth = l.lineWidth;
            ctx.strokeStyle = l.strokeStyle;
            ctx.strokeRect(l.startx, l.starty, l.width, l.height);
        }
        if (l.isFill){
            ctx.fillStyle = l.fillStyle;
            ctx.fillRect(l.startx, l.starty, l.width, l.height);
        }
  });
  canvas_data.circle.forEach(function(l) {
    ctx.beginPath();
    ctx.arc(Math.abs(l.endx + l.startx)/2, Math.abs(l.endy + l.starty)/2,
        Math.sqrt(Math.pow(l.endx - l.startx, 2) + Math.pow(l.endy - l.starty, 2))/2, 0, pi2, true);
    if (l.isStroke){
        ctx.lineWidth = l.lineWidth;
        ctx.strokeStyle = l.strokeStyle;
        ctx.stroke();
    }
    if (l.isFill){
        ctx.fillStyle = l.fillStyle;
        ctx.fill();
        }
  });


}



function savepaint(){
    var filename = document.getElementById("fname").value;
    var link = document.createElement('a');
    link.download = filename + '.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
    link.delete;
}