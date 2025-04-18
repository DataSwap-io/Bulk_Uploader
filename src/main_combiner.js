// main.js

const { main_vidgen } = require('./main_vidgen');
const { exec } = require('child_process');
const util = require('util');
const path = require('path');
const fs = require('fs');
const execPromise = util.promisify(exec);

const dopamineVideoPath = 'C:\\Users\\Moussa\\Downloads\\Youtube_vid-main\\Youtube_vid-main\\src\\DopamineVid\\video.mp4';
const outputDir = path.join(__dirname, 'outputvid');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir);
}

async function removeFileIfExists(filePath) {
  if (fs.existsSync(filePath)) {
    try {
      await fs.promises.chmod(filePath, 0o666);
      await fs.promises.unlink(filePath);
      console.log(`Bestand verwijderd: ${filePath}`);
    } catch (err) {
      console.error(`Fout bij verwijderen van ${filePath}:`, err.message);
    }
  }
}

async function getVideoDuration(filePath) {
  try {
    const { stdout } = await execPromise(`ffprobe -v error -show_entries format=duration -of csv="p=0" "${filePath}"`);
    return parseFloat(stdout);
  } catch (err) {
    console.error(`Fout bij ophalen duur voor ${filePath}:`, err.message);
    throw err;
  }
}

async function getRandomClipFromDopamine(duration, outputFileName) {
  const outputPath = path.join(__dirname, outputFileName);
  await removeFileIfExists(outputPath);

  const totalDuration = await getVideoDuration(dopamineVideoPath);
  if (totalDuration < duration) {
    throw new Error("Het DopamineVid bestand is korter dan de benodigde clipduur.");
  }
  const maxStart = totalDuration - duration;
  const randomStart = Math.random() * maxStart;
  const command = `ffmpeg -ss ${randomStart} -i "${dopamineVideoPath}" -t ${duration} -c copy "${outputPath}" -y`;
  console.log(command);
  console.log(`Knip random Dopamine clip: start=${randomStart.toFixed(2)} sec, duur=${duration.toFixed(2)} sec`);
  try {
    await execPromise(command);
    console.log(`Random clip aangemaakt: ${outputPath}`);
  } catch (err) {
    console.error("Fout bij knippen random clip:", err.message);
    throw err;
  }
}

async function mergeClips(clip1Path, clip2Path, outputFileName) {
    const outputPath = path.join(outputDir, outputFileName);
    await removeFileIfExists(outputPath);
  
    const outputWidth = 1080;
    const outputHeight = 1920;
  
    const command = `ffmpeg -i "${clip1Path}" -i "${clip2Path}" -filter_complex ` +
      `"[0:v]scale=1080:1280:force_original_aspect_ratio=increase,crop=1080:1280,` +
      `setpts=PTS-STARTPTS[top]; ` +
      `[1:v]scale=1080:640:force_original_aspect_ratio=increase,crop=1080:640,` +
      `setpts=PTS-STARTPTS[bottom]; ` +
      `[top][bottom]vstack=inputs=2[v]; ` +
      `[0:a]aresample=async=000,asetpts=PTS-STARTPTS,adelay=000|000[a0]; ` + // ⭐ async=500 & adelay=300
      `[1:a]aresample=async=000,asetpts=PTS-STARTPTS[a1]; ` + // ⭐ async=500
      `[a0][a1]amix=inputs=2:duration=longest:dropout_transition=0[a]" ` + // ⭐ duration=longest
      `-map "[v]" -map "[a]" ` +
      `-c:v libx264 -preset veryfast -crf 23 -r 30 ` +
      `-c:a aac -b:a 192k ` + // ⭐ Verwijder -shortest
      `-fflags +genpts -movflags +faststart "${outputPath}" -y`;
  
    console.log(`Creating Shorts video in ${outputPath}`);
    try {
      await execPromise(command);
      console.log(`Video successfully created: ${outputPath}`);
    } catch (err) {
      console.error("Error merging clips:", err.message);
      throw err;
    }
  }

  
async function processClips() {
  const tempFiles = [];

  try {
    const link = 'N9Ff6WBP-2A';
    const result = await main_vidgen(link);
    tempFiles.push(result.filePath);
    const clipNames = result.clips;

    for (let clipName of clipNames) {
      const clipPath = path.join('gedownloade_vids', clipName);
      tempFiles.push(clipPath);

      const duration = await getVideoDuration(clipPath);
      console.log(`Duur van ${clipName}: ${duration.toFixed(2)} seconden`);

      const randomClipName = `random_${clipName}`;
      await getRandomClipFromDopamine(duration, randomClipName);
      tempFiles.push(path.join(__dirname, randomClipName));

      const outputFileName = `youtube_short_${clipName}`;
      await mergeClips(clipPath, randomClipName, outputFileName);
    }
  } catch (err) {
    console.error("Fout tijdens het verwerken van clips:", err.message);
  } finally {
    console.log("Cleanup: verwijderen van tussenbestanden.");
    for (const filePath of tempFiles) {
      try {
        await removeFileIfExists(filePath);
      } catch (err) {
        console.error(`Fout bij verwijderen van ${filePath}:`, err.message);
      }
    }
  }
}

processClips();