import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';
import * as fs from 'fs';

const execPromise = promisify(exec);

@Injectable()
export class PythonScriptService {
  async runPythonScript(biosIds: string[], fileName: string): Promise<any> {
    // biosIds'yi JSON formatında bir dosyaya yazalım
    const filePath = join(process.cwd(), 'src', 'pythoncodes', 'bios_ids.json');
    fs.writeFileSync(filePath, JSON.stringify(biosIds, null, 2));

    // Python script'inin tam yolunu belirleyelim
    const scriptPath = join(
      process.cwd(),
      'src',
      'pythoncodes',
      'app.py',
    ).replace(/\\/g, '/');

    // Python betiğini çalıştırırken JSON dosyasının yolunu argüman olarak gönderelim
    const command = `python ${scriptPath} ${filePath} ${fileName}`;

    try {
      const { stdout, stderr } = await execPromise(command);
      if (stderr) {
        throw new Error(`Python error: ${stderr}`);
      }
      return stdout;
    } catch (error) {
      throw new Error(`Error executing Python script: ${error.message}`);
    }
  }
}
