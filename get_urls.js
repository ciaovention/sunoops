function downloadTextAsFile(filename, text) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.style = 'display: none';
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
}

function extractUrlsFromCurrentPage() {
    try {
        const gridElement = document.querySelector('[role="grid"]');
        const reactPropsKey = Object.keys(gridElement).find(key => key.startsWith('__reactProps'));

        if (!reactPropsKey) return '';

        const collection = gridElement[reactPropsKey].children[0].props.values[0][1].collection;
        const urls = [...collection]
            .filter(item => item.value.audio_url || item.value.video_url)
            .map(item => {
                const title = item.value.title.trim() || item.value.id;
                const audio = item.value.audio_url ? `${title}.mp3|${item.value.audio_url}` : '';
                const video = item.value.video_url ? `${title}.mp4|${item.value.video_url}` : '';
                return [audio, video].filter(Boolean).join("\n");
            })
            .join("\n");

        return urls;
    } catch (error) {
        console.error('Error extracting URLs:', error);
        return '';
    }
}

function scrapeAndDownload() {
    const urls = extractUrlsFromCurrentPage();
    const numberOfLines = urls.split("\n").length;

    if (urls) {
        downloadTextAsFile('urls.txt', urls);
    } else {
        console.warn('No URLs extracted. Skipping download.');
    }

    if (numberOfLines > 39) {
        const nextPageButton = document.querySelector('button svg path[d="M246.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-128-128c-9.2-9.2-22.9-11.9-34.9-6.9s-19.8 16.6-19.8 29.6l0 256c0 12.9 7.8 24.6 19.8 29.6s25.7 2.2 34.9-6.9l128-128z"]');

        if (nextPageButton) {
            nextPageButton.closest('button').click();
            setTimeout(scrapeAndDownload, 5000); // Wait for the page to load
        } else {
            console.log('No more pages found or reached the last page.');
        }
    } else {
        console.log('Fewer than 40 lines extracted. Stopping navigation.');
    }
}

// Start the process
scrapeAndDownload();