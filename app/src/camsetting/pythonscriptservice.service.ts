import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';

const execPromise = promisify(exec);

@Injectable()
export class PythonScriptService {
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
    console.log(command);

    try {
      const { stdout, stderr } = await execPromise(command, {
        encoding: 'utf-8',
      });
      if (stderr) {
        throw new Error(`Python error: ${stderr}`);
      }
      return stdout; // Python betiğinden gelen çıktıyı döndür
    } catch (error) {
      throw new Error(`Error executing Python script: ${error.message}`);
    }
  }
}
