let model = null

function parseContainer(line) {
    if (line.trim() === "") {
        return
    }

    const [width, length, height] = line.split(" ").map(Number)

    return {width, length, height}
}

function parseBox(line) {
    if (line.trim() === "") {
        return
    }

    const [x,y,z,dx,dy,dz,type] = line.split(" ").map(Number)

    return {x, y, z, dx, dy, dz, type}
}

function parseDescription(desc) {
    const [dataset, id, leftBox, leftVol, usage] = desc.split(" ")

    return {
        dataset,
        id,
        leftBox: Number(leftBox),
        leftVol: Number(leftVol),
        usage,
    }
}

function parseModel(input) {
    const [desc, in_cont, ...in_boxes] = input.split(/[;\n]/)

    return {
        description: parseDescription(desc),
        container: parseContainer(in_cont),
        boxes: in_boxes.map(parseBox).filter(Boolean), 
    }
}

function updateModel() {
    new_model = true
    const input = document.getElementById("input_text").value

    const parsedModel = parseModel(input)

    model = parsedModel
}


function drawContainer(W, L, H) {
    sideColor = color(225, 225, 225)
    sideColor.setAlpha(64)

    fill(sideColor)

    const sides = [
        // LENGTH x HEIGHT
        [[-1,-1,-1], [-1,-1, 1], [-1, 1, 1], [-1, 1,-1]],
        [[ 1,-1,-1], [ 1,-1, 1], [ 1, 1, 1], [ 1, 1,-1]],

        // WIDTH x HEIGHT
        [[-1,-1,-1], [-1,-1, 1], [ 1,-1, 1], [ 1,-1,-1]],
        [[-1, 1,-1], [-1, 1, 1], [ 1, 1, 1], [ 1, 1,-1]],
    ]

    const drawCorner = (d) => ([x,y,z]) => {
        vertex(x * W/2, y * L/2, z * H/2 - d)
    }

    sides.forEach(side => {
        push()
        noFill()
        beginShape()
        side.forEach(drawCorner(0))
        endShape(CLOSE)
        pop()
    })


    const base = [[-1,-1,-1], [ 1,-1,-1], [ 1, 1,-1], [-1, 1,-1]]

    push()
    fill(128)
    beginShape()
    base.forEach(drawCorner(1))
    endShape(CLOSE)
    pop()
}

const COLORS = [
    '#a6cee3',
    '#1f78b4',
    '#b2df8a',
    '#33a02c',
    '#fb9a99',
    '#e31a1c',
    '#fdbf6f',
    '#ff7f00',
    '#cab2d6',
    '#6a3d9a',
    '#ffff99',
    '#b15928',
    '#8dd3c7',
    '#ffffb3',
    '#bebada',
    '#fb8072',
    '#80b1d3',
    '#fdb462',
    '#b3de69',
    '#fccde5',
    '#d9d9d9',
    '#bc80bd',
    '#ccebc5',
]

function drawBox(cont, b) {
    const {width: W, length: L, height: H} = cont
    const {x,y,z,dx,dy,dz,type} = b
    const color = COLORS[type % COLORS.length]

    const coord = (D, p, dp) => p + dp/2 - D/2

    push()
    fill(color)
    translate(
        coord(W,x,dx),
        coord(L,y,dy),
        coord(H,z,dz),
    )
    box(dx,dy,dz)
    pop()
}

const drawBoxes = (container, boxes) => boxes.forEach(b => drawBox(container, b))

let WIDTH
let HEIGHT
function setup() {
    const main = document.querySelector('#main');
    WIDTH = main.offsetWidth
    HEIGHT = main.offsetHeight

    createCanvas(WIDTH, HEIGHT, WEBGL)
    createEasyCam()
}

function getDescriptionText(model) {
    if (!model || !model.description) {
        return 'Error, wrong input data'
    }
    const {dataset, id, leftBox, leftVol, usage} = model.description

    const volume /*in m^3 */ = leftVol / (100 * 100 * 100)

    const formatedVol = volume.toPrecision(3)
    return [
        `Instance: ${dataset}-${id}`,
        `Usage: ${usage}%`,
        `Left boxes: ${leftBox}`,
        `Left vol.: ${formatedVol} m²`,
    ].join(' ')
}

let new_model = false

function draw() {
    const description = document.getElementById('description')

    background(220)

    if (!model || !model.container || !model.boxes) {
        if (new_model) {
            description.innerText = 'No packaging layout data'
        }
        return
    }

    const {boxes, container} = model
    const {width, length, height} = container

    if (new_model) {
        description.innerText = getDescriptionText(model)
    }

    drawContainer(width, length, height)

    drawBoxes(container, boxes)

    // Allow rotating by mouse
    orbitControl(1, 1, 0.01)

    new_model = false
}
