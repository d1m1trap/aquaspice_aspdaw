async function sendDataForm(dt) {
    try {
        const response = await fetch('/get_historical', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dt)
        });
        // fetch('/static/resp.json'); // test
        const json = await response.json();
        document.getElementById('download_data_btn').classList.remove("disabled");
        return json;
    } catch (error) {
        console.error('Error:', error);
    }
}

function createTable(data, index_name = "Datetime") {
    let attributes = data.attributes;
    let index = data.index;
    console.log("createTable!!!!!!!!!!!!!!", attributes);

    let data_preview_table = document.getElementById('data_preview_table');
    data_preview_table.innerHTML = '';

    // Create thead and tbody elements
    let thead = document.createElement('thead');
    let tbody = document.createElement('tbody');

    // Creating header row
    let headerRow = document.createElement('tr');
    let th = document.createElement('th');
    th.classList.add("mdl-data-table__cell--non-numeric");
    th.textContent = index_name;
    headerRow.appendChild(th);

    attributes.forEach(attr => {
        let th = document.createElement('th');
        th.classList.add("mdl-data-table__cell--non-numeric");
        th.textContent = attr.attrName;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Creating body rows
    index.forEach((val, idx) => {
        let tr = document.createElement('tr');
        let td = document.createElement('td');
        td.classList.add("mdl-data-table__cell--non-numeric");
        td.textContent = val;
        tr.appendChild(td);

        attributes.forEach(attr => {
            let td = document.createElement('td');
            td.classList.add("mdl-data-table__cell");
            td.textContent = attr.values[idx];
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    // Append thead and tbody to the table
    data_preview_table.appendChild(thead);
    data_preview_table.appendChild(tbody);
};


// Function to create table rows
// function createTableRows(attributes, indices) {
//     const tbody = document.querySelector("#data_preview_table tbody");
//
//     indices.forEach((index, idx) => {
//         const tr = document.createElement('tr');
//
//         // Add index cell
//         const indexTd = document.createElement('td');
//         indexTd.textContent = index;
//         tr.appendChild(indexTd);
//
//         // Add other attribute cells
//         attributes.forEach(attr => {
//             const td = document.createElement('td');
//             td.textContent = attr.values[idx]; // Assumes each attribute has values for each index
//             tr.appendChild(td);
//         });
//
//         tbody.appendChild(tr);
//     });
// }

function downloadCSVData() {
    console.log("downloadCSVData");
    // alert("OK");
    fetch('/download-csv-data').then(response => response.blob())
        .then(blob => {
            // Create a new URL for the blob
            const url = window.URL.createObjectURL(blob);

            // Create a link to download it
            const a = document.createElement('a');
            a.href = url;
            a.download = 'data_export.csv';
            document.body.appendChild(a);
            a.click();

            // Remove the link and revoke the URL
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Download error:', error));
}


document.addEventListener("DOMContentLoaded", (event) => {

    var options = {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
    }
    const fp_from = flatpickr("#date_from", options);
    const fp_to = flatpickr("#date_to", options);


    var experimentDataForm = document.getElementById("experiment_data");
    experimentDataForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const formEntries = new FormData(experimentDataForm).entries();
        const json = Object.assign(...Array.from(formEntries, ([x, y]) => ({[x]: y})));
        return sendDataForm(json).then(resp => {
            console.log("general resp: ", resp);
            if (resp) {
                let slicedData = {
                    attributes: resp.attributes.map(attr => ({...attr, values: attr.values.slice(0, 10)})),
                    index: resp.index.slice(0, 10)
                };
                return createTable(slicedData);
            }
        }).catch(e => {
            return {"error": e};
        });
    });

    var DownloadDataForm = document.getElementById("download_data");
    DownloadDataForm.addEventListener("submit", function (e) {
        e.preventDefault();
        downloadCSVData();
        return true;
    });
    return true;
});

