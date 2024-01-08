const processes = [
    {
        "id": 2,
        "name": "stream cracker process streams",
        "pilot_id": 2,
        "assets": [
            {
                "id": 6,
                "name": "biological activated carbon",
                "process_id": 2
            },
            {
                "id": 7,
                "name": "mixed bed",
                "process_id": 2
            },
            {
                "id": 8,
                "name": "reverse osmosis",
                "process_id": 2
            },
            {
                "id": 9,
                "name": "storage tank",
                "process_id": 2
            },
            {
                "id": 10,
                "name": "ultrafiltration",
                "process_id": 2
            }
        ]
    },
    {
        "id": 3,
        "name": "cooling towers",
        "pilot_id": 2,
        "assets": [
            {
                "id": 11,
                "name": "splitter",
                "process_id": 3
            },
            {
                "id": 12,
                "name": "cooling tower a",
                "process_id": 3
            },
            {
                "id": 13,
                "name": "cooling tower b",
                "process_id": 3
            },
            {
                "id": 14,
                "name": "cooling tower c",
                "process_id": 3
            },
            {
                "id": 15,
                "name": "cooling tower d",
                "process_id": 3
            },
            {
                "id": 16,
                "name": "cooling tower e",
                "process_id": 3
            },
            {
                "id": 17,
                "name": "collector",
                "process_id": 3
            }
        ]
    },
    {
        "id": 4,
        "name": "reverse osmosis concentrate",
        "pilot_id": 2,
        "assets": [
            {
                "id": 18,
                "name": "mix",
                "process_id": 4
            },
            {
                "id": 19,
                "name": "mixed bed",
                "process_id": 4
            },
            {
                "id": 20,
                "name": "pulsed flow reverse osmosis",
                "process_id": 4
            },
            {
                "id": 21,
                "name": "reverse osmosis",
                "process_id": 4
            },
            {
                "id": 22,
                "name": "softner",
                "process_id": 4
            },
            {
                "id": 23,
                "name": "treated water",
                "process_id": 4
            }
        ]
    }
];


function findById(data, id) {
    return processes.find(data => data.id === id);
}

function getProcesses() {
    fetch('/get-processes', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch((error) => console.error('Error:', error));
}


function sendProcessAsset(process, asset) {
    console.log("sendProcessAsset");
    fetch('/get-drawer-values', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({process: process, asset: asset})
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch((error) => console.error('Error:', error));
}


function populateAssetDropdown(assets, process, pilot="Agricola") {
    console.log("populateAssetDropdown");
    let assetInput = document.getElementById('asset_input');
    let assetDropdown = document.getElementById('asset-dropdown');
    assetDropdown.innerHTML = '';
    assetInput.value = '';
    assetInput.parentNode.classList.remove("disabled");
    assets.forEach(function (asset) {
        let li = document.createElement('li');
        li.className = 'mdl-menu__item';
        li.textContent = asset.name;
        li.onclick = function () {
            assetInput.value = asset.name;
            assetInput.parentNode.classList.add("is-dirty");
            assetDropdown.parentNode.classList.remove('is-visible');
            sendProcessAsset(process, assetInput.value);
            let sheader = document.getElementById('session-dependant-header');
            sheader.innerHTML = pilot+" "+process+" "+ asset.name;

        };
        assetDropdown.appendChild(li);
    });
}

function populateProcessDropdown(processes) {
    console.log("populateProcessDropdown");
    let processDropdown = document.getElementById('process-dropdown');
    processDropdown.innerHTML = ''; // Clear existing items

    processes.forEach(function (process) {
        var li = document.createElement('li');
        li.className = 'mdl-menu__item';
        li.textContent = process.name;
        li.dataset.value = process.name;
        li.onclick = function () {
            document.getElementById('process_input').value = process.name;
            document.getElementById('process_input').parentNode.classList.add("is-dirty");
            populateAssetDropdown(process.assets, process.name);
        };
        processDropdown.appendChild(li);
    });
}



document.addEventListener("DOMContentLoaded", function () {
    populateProcessDropdown(processes);
});



