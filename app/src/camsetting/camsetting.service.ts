/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { TokenDto } from './dto/token.dto';
import { PythonScriptService } from './pythonscriptservice.service';
import * as fs from 'fs';
import { resolve } from 'path';

@Injectable()
export class CamsettingService {
  constructor(private pythonService: PythonScriptService) {}

  async getCamera(tokendto: TokenDto): Promise<any> {
    try {
      const token = tokendto.token;
      const response = await fetch(
        'https://pts.mangobulut.com/apib/camera/record-capture-time?order=ASC',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        },
      );
      if (!response.ok) throw new UnauthorizedException();
      const data = await response.json();
      return data;
      //const biosIds = data.map((item) => item.biosId);
      // return this.pythonService.runPythonScript(data, 'Cameras');
    } catch (error) {
      console.error(
        'Error occurred while fetching data or running Python script:',
        error,
      );
      throw error;
    }
  }

  async getNode(tokenDto: TokenDto): Promise<any> {
    try {
      const token = tokenDto.token;
      const response = await fetch('https://pts.mangobulut.com/apib/node', {
        method: 'Get',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new UnauthorizedException();

      const data = await response.json();
      return data;
      // return this.pythonService.runPythonScript(data, 'Nodes');
    } catch (error) {
      console.error(
        'Error occurred while fetching data or running Python script:',
      );
      throw error;
    }
  }

  async getSubNode(tokendto: TokenDto): Promise<any> {
    try {
      const token = tokendto.token;
      const response = await fetch('https://pts.mangobulut.com/apib/sub-node', {
        method: 'Get',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new UnauthorizedException();

      const data = await response.json();
      return data;
      // return this.pythonService.runPythonScript(data, 'Sub-Nodes');
    } catch (error) {
      console.error(
        'Error occurred while fetching data or running Python script:',
      );
      throw error;
    }
  }

  async getLogs(): Promise<any> {
    try {
      const logsDir = resolve(process.cwd(), 'logs');
      const filePath = resolve(logsDir, 'script_logs.txt');
      const fileData = await fs.promises.readFile(filePath, 'utf-8');

      // STDOUT kısmındaki tüm logları ayırıyoruz
      const logsSections = fileData.split('STDOUT:').slice(1); // İlk 'STDOUT:'dan sonrasını alıyoruz

      const allLogs = logsSections
        .map((logSection) => {
          // Her bir log kısmını işlerken, STDERR kısmına kadar olan kısmı alıyoruz
          const logData = logSection.split('STDERR:')[0].trim();

          // Logu JSON'a dönüştürme
          try {
            return JSON.parse(logData);
          } catch (error) {
            console.error('Error parsing log data:', error);
            return null; // Eğer parse edilemezse null dönebiliriz
          }
        })
        .filter((log) => log !== null); // Null olmayanları filtrele

      return allLogs;
    } catch (error) {
      console.error('Error reading or parsing the log file:', error);
      throw new Error('Failed to retrieve script logs');
    }
  }
}
