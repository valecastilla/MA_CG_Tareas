/*
 * Script to read a model stored in Wavefront OBJ format
 *
 * Valentina Castilla
 */

'use strict';

/*
 * Read the contents of an OBJ file received as a string
 * Return an object called arrays, with the arrays necessary to build a
 * Vertex Array Object (VAO) for WebGL.
 */
function loadObj(objString) {

    // Object to store the data read from the OBJ file
    let objData = {
        vertices: [ ],
        normals: [ ],
        indices: [ ], // indexes for faces
        normalIndices: [ ]
    };
    // The array with the attributes that will be passed to WebGL
    let arrays = {
        a_position: {
            numComponents: 3,
            data: [ ]
        },
        a_color: {
            numComponents: 4,
            data: [ ]
        },
        a_normal: {
            numComponents: 3,
            data: [ ]
        },
        // Faces, indexes to form triangles
        indices:  { 
            numComponents: 3, 
            data: [ ] 
        }
    };

    let lines = objString.split('\n'); // Split the string into lines
    for (let line of lines) {
        line = line.trim();
        if (!line) continue;              // optional, skip empty lines
        let parts = line.split(/\s+/); 
        // If the first element of the line is 'v', its a vertex
        if (parts[0] === 'v') { 
            // Vertex position
            objData.vertices.push(
                parseFloat(parts[1]),
                parseFloat(parts[2]),
                parseFloat(parts[3])
            );
        }
        else if (parts[0] === 'vn') {
            // Vertex normal
            objData.normals.push(
                parseFloat(parts[1]),
                parseFloat(parts[2]),
                parseFloat(parts[3])
            );
        }
        else if (parts[0] === 'f') {
            // Since faces have indexes for how faces are connected and what normal each face has,
            // separate indexes for vertices and normals
            for (let i = 1; i <= 3; i++) {
                let indices = parts[i].split('//'); // Split the vertex and normal indices
                objData.indices.push(parseInt(indices[0]) - 1); // Convert to int, since OBJ indexes start at 1, subtract 1
                objData.normalIndices.push(parseInt(indices[1]) - 1);
            }
        }
    }

    // For every index in the faces array
    for (let i = 0; i < objData.indices.length; i++) {
        let vertexIndex = objData.indices[i]; // Get the vertex index
        //Add the vertex position to the position array
        arrays.a_position.data.push(
            objData.vertices[vertexIndex * 3],
            objData.vertices[vertexIndex * 3 + 1],
            objData.vertices[vertexIndex * 3 + 2]
        );
        // For now, assign a random color to each vertex
        arrays.a_color.data.push(
            Math.random(),
            Math.random(),
            Math.random(),
            1.0
        );
        let normalIndex = objData.normalIndices[i]; // Get the normal index
        // Add the normal to the normal array
        arrays.a_normal.data.push(
            objData.normals[normalIndex * 3],
            objData.normals[normalIndex * 3 + 1],
            objData.normals[normalIndex * 3 + 2]
        );

        arrays.indices.data.push(i);
    }

    return arrays;
}

// /*
//  * Read the contents of an MTL file received as a string
//  * Return an object containing all the materials described inside,
//  * with their illumination attributes.
//  */
// function loadMtl(mtlString) {


//     return /* SOMETHING */;
// }

// function main() {
//     const objText = 
//     `v -1.0 -1.0  1.0
//     v  1.0 -1.0  1.0
//     v  1.0  1.0  1.0
//     v -1.0  1.0  1.0
//     v -1.0 -1.0 -1.0
//     v -1.0  1.0 -1.0
//     v  1.0  1.0 -1.0
//     v  1.0 -1.0 -1.0
//     v -1.0  1.0 -1.0
//     v -1.0  1.0  1.0
//     v  1.0  1.0  1.0
//     v  1.0  1.0 -1.0
//     v -1.0 -1.0 -1.0
//     v  1.0 -1.0 -1.0
//     v  1.0 -1.0  1.0
//     v -1.0 -1.0  1.0
//     v  1.0 -1.0 -1.0
//     v  1.0  1.0 -1.0
//     v  1.0  1.0  1.0
//     v  1.0 -1.0  1.0
//     v -1.0 -1.0 -1.0
//     v -1.0 -1.0  1.0
//     v -1.0  1.0  1.0
//     v -1.0  1.0 -1.0
//     vn  0.0  0.0  1.0
//     vn  0.0  0.0 -1.0
//     vn  0.0  1.0  0.0
//     vn  0.0 -1.0  0.0
//     vn  1.0  0.0  0.0
//     vn -1.0  0.0  0.0
//     f  1//1  2//1  3//1
//     f  1//1  3//1  4//1
//     f  5//2  6//2  7//2
//     f  5//2  7//2  8//2
//     f  9//3 10//3 11//3
//     f  9//3 11//3 12//3
//     f 13//4 14//4 15//4
//     f 13//4 15//4 16//4
//     f 17//5 18//5 19//5
//     f 17//5 19//5 20//5
//     f 21//6 22//6 23//6
//     f 21//6 23//6 24//6 `;

//     const arrays = loadObj(objText);
//     console.log("arrays");
//     for (let i = 0; i < arrays.indices.data.length; i++) {
//         console.log(arrays.indices.data[i]);
//     }
//     console.log("vertex positions:");
//     for (let i = 0; i < arrays.a_position.data.length; i++) {
//         console.log(arrays.a_position.data[i]);
//     }
//     console.log("normals:");
//     for (let i = 0; i < arrays.a_normal.data.length; i++) {
//         console.log(arrays.a_normal.data[i]);
//     }
// }
// main();

//export { loadObj, loadMtl };
export { loadObj }