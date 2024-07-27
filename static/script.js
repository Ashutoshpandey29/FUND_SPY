document.addEventListener('DOMContentLoaded', (event) => {
    const typewriterContainer = document.querySelector('.typewriter');
    const texts = ["Generate fund trail reports efficiently!", "Analyze fund performance with ease!", "Compare funds with just a few clicks!", "Flag funds for further review!", "Track fund performance over time!"];
    let index = 0;

    const updateText = () => {
        typewriterContainer.innerHTML = ''; // Clear existing content
        const h2 = document.createElement('h2');
        h2.textContent = texts[index];
        typewriterContainer.appendChild(h2);
    };

    updateText(); // Initialize with the first text

    typewriterContainer.addEventListener('animationiteration', () => {
        index = (index + 1) % texts.length;
        updateText();
    });
});
