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
    ipAddresses: { biosid: string; ipAddress: string }[],
  ): Promise<any> {
    // ipAddresses dizisini JSON formatına dönüştürmek
    const ipAddressesArg = JSON.stringify(ipAddresses); // Doğrudan JSON string'e dönüştürülür

    // Python script'inin tam yolunu belirleyelim
    const scriptPath = join(
      process.cwd(),
      'src',
      'pythoncodes',
      'seleniumapp.py',
    ).replace(/\\/g, '/');

    // Python betiğini çalıştırırken JSON verisini argüman olarak gönderelim
    const command = `python ${scriptPath} "${ipAddressesArg.replace(/"/g, '\\"')}"`;
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
