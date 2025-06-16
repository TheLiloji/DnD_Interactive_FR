// Fonction pour lancer un dé
function rollD20() {
    const result = Math.floor(Math.random() * 20) + 1;
    const resultElement = document.getElementById('dice-result');
    resultElement.textContent = `Résultat du D20 : ${result}`;
    resultElement.style.display = 'block';
}

// Gestion de l'histoire interactive
const storyStates = {
    debut: {
        text: "Vous vous trouvez dans une taverne animée. L'ambiance est chaleureuse, et plusieurs options s'offrent à vous.",
        choices: [
            {text: "Parler au tavernier", next: "tavernier"},
            {text: "Observer les autres clients", next: "observer"},
            {text: "Voler discrètement une chope", next: "voler"}
        ]
    },
    tavernier: {
        text: "Le tavernier est un homme robuste au sourire accueillant. 'Que puis-je pour vous ?' demande-t-il.",
        choices: [
            {text: "Commander une bière", next: "commander"},
            {text: "Demander des rumeurs", next: "rumeurs"},
            {text: "Retourner à votre place", next: "debut"}
        ]
    },
    observer: {
        text: "Vous remarquez un groupe de mercenaires dans un coin et un mystérieux personnage encapuchonné au bar.",
        choices: [
            {text: "Approcher les mercenaires", next: "mercenaires"},
            {text: "Observer le personnage mystérieux", next: "mysterieux"},
            {text: "Retourner à votre observation initiale", next: "debut"}
        ]
    },
    voler: {
        text: "Vous tentez de voler une chope... Un jet de Dextérité serait approprié ici !",
        choices: [
            {text: "Faire un jet de Dextérité", next: "debut"},
            {text: "Abandonner l'idée", next: "debut"}
        ]
    }
};

function updateStory(stateKey) {
    const state = storyStates[stateKey];
    const container = document.getElementById('story-container');
    
    if (!state) return;

    container.innerHTML = `
        <p>${state.text}</p>
        <div class="choices">
            ${state.choices.map(choice => `
                <button class="choice-button" onclick="updateStory('${choice.next}')">
                    ${choice.text}
                </button>
            `).join('')}
        </div>
    `;
}

// Fonction pour sauvegarder les modifications du personnage
function saveCharacter(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const characterData = Object.fromEntries(formData);

    fetch(form.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(characterData)
    })
    .then(response => response.json())
    .then(data => {
        alert('Personnage sauvegardé !');
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la sauvegarde');
    });
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    const storyContainer = document.getElementById('story-container');
    if (storyContainer) {
        updateStory('debut');
    }

    const characterForm = document.getElementById('character-form');
    if (characterForm) {
        characterForm.addEventListener('submit', saveCharacter);
    }
}); 