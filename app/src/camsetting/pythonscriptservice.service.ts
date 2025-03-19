/* eslint-disable @typescript-eslint/no-unsafe-member-access */
import { Injectable, Logger } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { join, resolve } from 'path';
import { writeFile, mkdir } from 'fs/promises';

const execPromise = promisify(exec);

@Injectable()
export class PythonScriptService {
  private readonly logger = new Logger(PythonScriptService.name);

  async runPythonScript(ipAddresses: { ipAddress: string }[]): Promise<any> {
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

      // Log dosyasına yazma işlemi
      const logFilePath = resolve(logsDir, 'script_logs.txt');
      const logEntry = `\n=== Execution Log ===\nCommand: ${command}\nSTDOUT: ${stdout}\nSTDERR: ${stderr}\n====================\n`;
      await writeFile(logFilePath, logEntry, { flag: 'a' });

      return { stdout, stderr };
    } catch (error) {
      this.logger.error(`Error executing Python script: ${error.message}`);
      //throw new Error(`Error executing Python script: ${error.message}`);
    }
  }
}
