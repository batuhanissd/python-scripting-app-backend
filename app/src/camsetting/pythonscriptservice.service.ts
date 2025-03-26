/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-call */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { Injectable, Logger } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { join, resolve } from 'path';
import { mkdir, appendFile } from 'fs/promises';

const execPromise = promisify(exec);

@Injectable()
export class PythonScriptService {
  private readonly logger = new Logger(PythonScriptService.name);

  async runPythonScript(
    processType: string,
    selectedCamera: { biosid: string; ipAddress: string }[],
  ): Promise<any> {
    // selectedCamera dizisini JSON formatına dönüştürmek
    const selectedCameraArg = JSON.stringify(selectedCamera); // Doğrudan JSON string'e dönüştürülür

    let pythonscript;
    switch (processType) {
      case 'motoron':
        pythonscript = 'phaseallmotorcycleon.py';
        break;
      case 'motoroff':
        pythonscript = 'phaseallmotorcycleoff.py';
        break;
      case 'ftpconfig':
        pythonscript = 'phaseallcameraftpconfig.py';
        break;
      case 'selenium':
        pythonscript = 'seleniumapp.py';
        break;
      default:
        throw new Error('Invalid processType selection');
    }
    // Python script'inin tam yolunu belirleyelim
    const scriptPath = join(
      process.cwd(),
      'src',
      'pythoncodes',
      `${pythonscript}`,
    ).replace(/\\/g, '/');

    // Python betiğini çalıştırırken JSON verisini argüman olarak gönderelim
    const command = `python ${scriptPath} "${selectedCameraArg.replace(/"/g, '\\"')}"`;
    this.logger.log(`Executing command: ${command}`);

    try {
      const { stdout, stderr } = await execPromise(command, {
        encoding: 'utf-8',
      });

      // Log stdout ve stderr çıktıları
      if (stdout) {
        this.logger.log(`Python script stdout: ${stdout}`);
      }
      if (stderr) {
        this.logger.error(`Python script stderr: ${stderr}`);
      }

      // Log klasörünü oluşturma (eğer yoksa)
      const logsDir = resolve(process.cwd(), 'logs');
      await mkdir(logsDir, { recursive: true });

      // Log dosyasının tam yolunu belirleyelim
      const logFilePath = resolve(logsDir, 'script_logs.txt');

      // stdout çıktısını JSON'a dönüştür
      const stdoutData = JSON.parse(stdout);

      // Her bir IP için logları tek dosyaya yazacağız
      stdoutData.forEach(async (entry) => {
        const logEntry = `\n=== Execution Log ===\nCommand: ${command}\nSTDOUT: ${JSON.stringify(entry, null, 4)}\nSTDERR: ${stderr ? stderr : ''}\n====================\n`;

        // Tek bir dosyaya ekleme yapıyoruz
        await appendFile(logFilePath, logEntry, { encoding: 'utf-8' });
      });

      return { stdout, stderr };
    } catch (error) {
      this.logger.error(`Error executing Python script: ${error.message}`);
    }
  }
}
