console.log("script.js loaded");

function getElements() {
  fetch('/get_element_table')
        .then(response => response.json())
        .then(elements => {
            const elementList = document.getElementById('element-list');
            elements.forEach(element => {
                const listItem = document.createElement('li');
                listItem.textContent = `Name: ${element.name}, Code: ${element.code}, ID: ${element.id}`;
                elementList.appendChild(listItem);
            });
        });
}

function populateMoleculeList() {
  fetch('/get_molecule')
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById('molecule_list');
      console.log(data)
      data.molecules.forEach(molecule => {
        const option = document.createElement('option');
        option.value = molecule.id;
        option.appendChild(document.createTextNode(`${molecule.name} (${molecule.num_atoms} atoms, ${molecule.num_bonds} bonds)`));
        select.appendChild(option);
      });
    });
}

function showMolecule() {
  const select = document.getElementById('molecule_list');
  const selectedOption = select.options[select.selectedIndex];
  const moleculeName = selectedOption.textContent.split('(')[0].trim();

  if (!moleculeName) {
    alert('Please select a molecule');
    return;
  }
  fetch('/display_molecule?name=' + moleculeName)
  .then(response => response.text())
  .then(svgString => {
    // Render the SVG string to the page
    const svgContainer = document.getElementById('molecule-display');
    svgContainer.innerHTML = svgString;
  });
}

document.addEventListener('DOMContentLoaded', function() {
  populateMoleculeList();
  getElements();
});