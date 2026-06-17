import WebSocket from "./websocket.js";


let ws = null;
let connected = false;

let auto = false;
let x = 0.0;
let y = 0;
let z = 0.0;
let lastX = 0.0;
let lastY = 0.0;
let lastZ = 0.0;


let delaycount = 0;
let speeds = [1.0, 1.0, 1.0];

let checkdetected = false;
let delay = 0;


register("command", () => {
    ws = new WebSocket("ws://localhost:6749");

    ws.onMessage = (msg) => {
        tag = msg.split("::")[0]
        content = msg.split("::")[1]
        if (tag === "(action)") {
            if (content === "setup") {
                const gardenLine = TabList.getNames().find(str => str.includes("§r§b§lArea: §r§7Garden§r"))
                if (gardenLine) {
                    lastX = new Entity(Player.getPlayer()).getLastX().toFixed(4);
                    lastY = new Entity(Player.getPlayer()).getLastY().toFixed(4);
                    lastZ = new Entity(Player.getPlayer()).getLastZ().toFixed(4);
                    x = Player.getX().toFixed(4);
                    y = Player.getY().toFixed(4);
                    z = Player.getZ().toFixed(4);  
                    speeds = [1.0, 1.0, 1.0];
                    
                    ws.send("(coord)::" + x + "," + y + "," + z);
                    ws.send("(log)::\nStarting Position : " + x + "," + y + "," + z);
                    ws.send("(action)::start");
                } else {
                    ChatLib.chat("Could not confirm whether on Garden, cancelling start.")
                    ws.send("(log)::Could not confirm whether on Garden, cancelling start.");
                }

            } else if (content === "stop") {
                ws.send("(action)::stop");
                auto = false;
                ChatLib.chat("Killed Auto")

            } else if (content === "start") {
                auto = true;
                ChatLib.chat("Started Auto");
            }
        } else if (tag === "(log)") ChatLib.chat(content);
    }

    ws.onError = (exception) => {
        ChatLib.chat("Error: " + exception);
    }

    ws.onOpen = () => {
        ChatLib.chat("Connected to Python socket.");
        connected = true;
    }

    ws.onClose = () => {
        ChatLib.chat("Disconnected from python socket.");
        connected = false;
        auto = false;
    }

    ws.connect();

}).setName("connectws").setAliases("cws");

register("command", () => {
    ws.close()
}).setName("disconnectws").setAliases("dcws");

// Position tracker for speed and lane changes
register("tick", () => {
    if (auto) {
        lastX = new Entity(Player.getPlayer()).getLastX().toFixed(4);
        lastY = new Entity(Player.getPlayer()).getLastY().toFixed(4);
        lastZ = new Entity(Player.getPlayer()).getLastZ().toFixed(4);
        
        x = Player.getX().toFixed(4);
        y = Player.getY().toFixed(4);
        z = Player.getZ().toFixed(4);

        if (connected && (z > 135 || z < -135)) {
            ws.send("(coord)::" + x + "," + y + "," + z); 
        }
    }
});

// Speed and direction tracker for macro checks
check = register("step", () => {
    if (auto) {
        // ChatLib.chat("Speed : " + addSpeed(Math.round(20 * distFormula(lastX, lastY, lastZ, x, y, z) * 10) / 10));
        addSpeed(Math.round(20 * distFormula(lastX, lastY, lastZ, x, y, z) * 10) / 10)
        
        if (Player.getYaw() != 90 || Player.getPitch() != 0 || speeds.every(num => num == 0.0)) {
            delaycount = 0;
            checkdetected = true;
            auto = false;
            delay = Math.floor((Math.random() * 80) + 80)
            ChatLib.chat("Response Delay : " + delay)
            playSound("macrocheck.ogg")
            if (speeds.every(num => num == 0.0)) {
                delay -= 70;
            }
            check.setFps(60)
            ChatLib.chat("hello")
        }
    }
    if (checkdetected) {
        if (delaycount++ == delay) {
            ws.send("(action)::stop")
            checkdetected = false;
            check.setFps(2)
        }
    }
}).setFps(2);

// Auto-stop when kicked
register("worldUnload", () => {
    if (auto) {
        ws.send("(action)::stop");
        auto = false;
    }
});

register("command", () => {
    checkPests()
}).setName("checkgard").setAliases("cg");

register("chat", () => {
    checkPests()
}).setCriteria("Farming Fortune has been reduced by").setContains();
  

function playSound(file) {
    let a  = new Sound({
        source : file,
        priority : true,
        volume : 0.5
    });
    a?.play();
}

function distFormula(x1, y1, z1, x2, y2, z2) {
    return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2);
}

function addSpeed(speed) {
    speeds.unshift(speed); // Add the new number to the beginning
    if (speeds.length > 3) {
        speeds.pop(); // Remove the last element if the length exceeds 5
    }
    return speeds;
}

// Precon : on garden
function checkPests() {
    const pestLine = TabList.getNames().find(str => str.includes("§r Alive: §r§4"))
    if (pestLine) {
        let pest = parseInt(pestLine.match(/§4(\d+)§r/)[1],10)
        if (pest > 2) {
            playSound("fourpest.ogg");
        }
    }
}