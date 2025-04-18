const { getMostReplayedParts } = require("./index.js");
const { downloadVideo } = require("./Youtube_Downloader.js");
const { exec } = require("child_process");
const util = require('util');
const execPromise = util.promisify(exec);

async function main_vidgen(link) {
    let downloadedFilePath;
    const clipNames = []; 

    try {
        const result = await downloadVideo(link);
        downloadedFilePath = result.filePath;
        console.log(result.filePath);
    } catch (err) {
        console.error("Fout bij downloaden:", err.message);
        throw err;
    }

    try {
        const data = await getMostReplayedParts(link, 9);
        await Promise.all(data.replayedParts.map((part, index) => {
            return new Promise((resolve, reject) => {
                const Start = part.start;
                const End = part.end;
                console.log(`Segment ${index}: ${Start} tot ${End}`);

                const duration = End - Start;
                const clipNum = String(index + 1).padStart(2, "0"); 
                const clipName = `clip_short_${clipNum}.mp4`;

                clipNames.push(clipName);

                // Gebruik re-encoding voor betere nauwkeurigheid bij startpunten
                // Zoek eerst de keyframe vóór de gewenste startpositie
                // Dit is wat accurater dan direct `-c copy` gebruiken
                const command = `ffmpeg -i "${downloadedFilePath}" -ss ${Start} -t ${duration} -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 128k "gedownloade_vids/${clipName}"`;
                
                exec(command, (error, stdout, stderr) => {
                    if (error) {
                        console.error(`Fout bij knippen van clip ${clipName}:`, error.message);
                        return reject(error);
                    } else {
                        console.log(`Clip gemaakt: ${clipName}`);
                        resolve();
                    }
                });
            });
        }));
    } catch (error) {
        console.error("Fout bij verwerken van segmenten:", error);
        throw error;
    }
    
    return {
        filePath: downloadedFilePath,
        clips: clipNames,
    };
}

module.exports = {
    main_vidgen,
};