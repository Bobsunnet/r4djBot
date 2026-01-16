function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Returns the correct word form based on the number.
 * @param {number} workDays - The quantity
 * @param {string[]} titles - Array of 3 forms: ['зміна', 'зміни', 'змін']
 */
function formatWorkDaysText(workDays, titles) {
    let pluralVariant = 0;
    const lastDigit = workDays%10;
    const lastTwoDigits = workDays%100;
    if (lastTwoDigits >= 11 && lastTwoDigits <= 19){
        pluralVariant = 2;
    }
    else if (lastDigit >= 2 && lastDigit <= 4) {
        pluralVariant = 1;
    }
    else if (lastDigit >= 5 || lastDigit === 0) {
        pluralVariant = 2;
    }
    return titles[pluralVariant]
}

export default { escapeHtml, formatWorkDaysText }
