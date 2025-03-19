/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import {
  Controller,
  Post,
  BadRequestException,
  Headers,
  Body,
} from '@nestjs/common';
import { CamsettingService } from './camsetting.service';
import { TokenDto } from './dto/token.dto';
import { PythonScriptService } from './pythonscriptservice.service';

@Controller('camsetting')
export class CamsettingController {
  constructor(
    private camsettingService: CamsettingService,
    private pythonScService: PythonScriptService,
  ) {}

  //Authorization header'ı doğrular ve token'ı döner.
  private extractToken(authHeader: string): TokenDto {
    if (!authHeader?.startsWith('Bearer ')) {
      throw new BadRequestException('Invalid or missing Authorization header');
    }

    const token = authHeader.slice(7).trim();
    if (!token) {
      throw new BadRequestException('Token is missing');
    }

    return { token };
  }

  @Post('/getcamera')
  async getCamera(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    return await this.camsettingService.getCamera(tokenDto);
  }

  @Post('/getnode')
  async getNode(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    return await this.camsettingService.getNode(tokenDto);
  }

  @Post('/getsubnode')
  async getSubnode(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    return await this.camsettingService.getSubNode(tokenDto);
  }

  @Post('/getaccesstoken')
  async getAccessToken(
    @Body() body: { ipAddresses: { ipAddress: string }[] },
    @Headers('authorization') authHeader: string,
  ): Promise<any> {
    this.extractToken(authHeader); // eger token yoksa ya da hataliysa hata firlatir.
    const ipAddresses = body.ipAddresses;
    console.log(ipAddresses);

    try {
      const result = await this.pythonScService.runPythonScript(ipAddresses);
      return { success: true, result };
    } catch (error) {
      console.error('Python script error:', error);
      return { success: false, message: error.message };
    }
  }

  @Post('/getlogs')
  async getLogs(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    if (tokenDto) {
      return await this.camsettingService.getLogs();
    }
  }
}
