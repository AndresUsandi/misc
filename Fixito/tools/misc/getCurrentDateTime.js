async function getCurrentDateTime() {
    try {
        const now = new Date();
        const dateString = now.toLocaleDateString(undefined, { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        const timeString = now.toLocaleTimeString(undefined, {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZoneName: 'short'
        });
        
        return `Current Date: ${dateString}\nCurrent Time: ${timeString}`;
    } catch (error) {
        return `Error getting date and time: ${error.message}`;
    }
}

export default getCurrentDateTime;
