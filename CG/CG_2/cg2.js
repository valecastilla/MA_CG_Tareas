/* 
    Valentina Castilla Melgoza A01028209
    20/11/2025
    CG_2
    Create a obj file with sides, height, base radius and top radius given as command line arguments
    Get vertices, faces and normals and return them in an OBJ file
*/

const fs = require("node:fs");

function generateCone(side, height, baseRadius, topRadius) {
    let vertices = [];
    let faces = [];

    // Add center points for base and top
    vertices.push([0, 0, 0]); // Base center
    vertices.push([0, height, 0]); // Top center
    let angleStep = (2 * Math.PI) / side;
    // Generate rest of vertices for base and top
    for (let s = 0; s < side; s++) {
        let angle = angleStep * s;
        let xBase = baseRadius * Math.cos(angle); // x = r * cos(angle)
        let zBase = baseRadius * Math.sin(angle); // z = r * sin(angle)
        let xTop = topRadius * Math.cos(angle);
        let zTop = topRadius * Math.sin(angle);
        vertices.push([xBase, 0, zBase]); // Use y axis for height, base at 0
        vertices.push([xTop, height, zTop]); // Top at specified height
    }
    // Generate faces for base, top and sides
    for (let s = 0; s < side; s++) {
        let n1 = s * 2 + 2;
        let n2 = ((s + 1) % side) * 2 + 2;
        let n3 = s * 2 + 3;
        let n4 = ((s + 1) % side) * 2 + 3;
        faces.push([n2, 0, n1]); // Base face
        faces.push([n3, 1, n4]); // Top face
        if (s === side - 1) {
            faces.push([n1, n3, n2]); // Side face 1 for last side, rotate
        } else {
            faces.push([n2, n1, n3]); // Side face 1
        }
        faces.push([n4, n2, n3]); // Side face 2
    }

    // Save info in objInfo for OBJ file
    let objInfo = [];
    // Add vertices to objInfo
    for (let i = 0; i < vertices.length; i++) {
        objInfo.push(`v ${vertices[i][0]} ${vertices[i][1]} ${vertices[i][2]}`); // Add vertex with obj format
    }
    // Helper vector operations
    function sub(a, b) {
        return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    } // Get vector a-b
    function cross(a, b) {
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        ];
    } // Cross product
    function len(a) {
        return Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]);
    } // Length of vector
    function normalize(a) {
        let L = len(a) || 1;
        return [a[0] / L, a[1] / L, a[2] / L];
    } // Normalize vector

    // Compute one normal per face. 
    let normals = [];
    for (let i = 0; i < faces.length; i++) {
        let f = faces[i];
        // Get vertices positions for face
        let p1 = vertices[f[0]];
        let p2 = vertices[f[1]];
        let p3 = vertices[f[2]];

        // Get normal for face
        // Face points downwards
        if (f.includes(0)) { 
            normals.push([0, -1, 0]); // All base faces have same normal
            continue;
        }
        // Face points upward
        if (f.includes(1)) {
            normals.push([0, 1, 0]); // All top faces have same normal
            continue;
        }
        // For all sides get normal
        let u = sub(p2, p1); // vector from p1 to p2
        let v = sub(p3, p1); // vector from p1 to p3
        let n = cross(u, v); // cross product of u and v
        n = normalize(n); // normalize the normal vector
        normals.push(n);
    }

    // Add normals to objInfo
    for (let i = 0; i < normals.length; i++) {
        objInfo.push(`vn ${normals[i][0]} ${normals[i][1]} ${normals[i][2]}`); // Add normal with obj format
    }

    // Add faces to objInfo
    for (let i = 0; i < faces.length; i++) {
        let f = faces[i];
        let ni = i + 1; // What normal index this face uses, they are in order
        let v1 = f[0] + 1; // Plus 1 to follow OBJ structure
        let v2 = f[1] + 1;
        let v3 = f[2] + 1;
        objInfo.push(`f ${v1}//${ni} ${v2}//${ni} ${v3}//${ni}`); // Add faces with obj format
    }

    // Funcion de chatgpt para guardar en un archivo OBJ
    function safe(x) {
        return String(x).replace(/\./g, "p");
    }
    const fname = `cone_s${side}_h${safe(height)}_b${safe(baseRadius)}_t${safe(
        topRadius
    )}.obj`;
    fs.writeFileSync(fname, objInfo.join("\n") + "\n", "utf8");
    console.log(`Wrote OBJ file: ${fname}`);
}

function main() {
    const args = process.argv.slice(2);

    // Default
    let sides = 8;
    let height = 6.0;
    let rBottom = 1.0;
    let rTop = 0.8;

    // Get values from command line arguments with restrictions
    if (args[0] !== undefined) {
        const s = parseInt(args[0]); 
        if (!Number.isNaN(s)) sides = Math.max(3, Math.min(36, s)); // Between 3 and 36
    }
    if (args[1] !== undefined) {
        const h = parseFloat(args[1]);
        if (!Number.isNaN(h) && h > 0) height = h;
    }
    if (args[2] !== undefined) {
        const rb = parseFloat(args[2]);
        if (!Number.isNaN(rb) && rb > 0) rBottom = rb;
    }
    if (args[3] !== undefined) {
        const rt = parseFloat(args[3]);
        if (!Number.isNaN(rt) && rt > 0) rTop = rt;
    }

    generateCone(sides, height, rBottom, rTop);
}

main();
