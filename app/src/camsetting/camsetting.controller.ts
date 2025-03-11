import { Controller, Post, BadRequestException, Headers } from '@nestjs/common';
import { CamsettingService } from './camsetting.service';
import { TokenDto } from './dto/token.dto';

@Controller('camsetting')
export class CamsettingController {
  constructor(private camsettingService: CamsettingService) {}

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
    return this.camsettingService.getCamera(tokenDto);
  }

  @Post('/getnode')
  async getNode(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    return this.camsettingService.getNode(tokenDto);
  }

  @Post('/getsubnode')
  async getSubnode(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    return this.camsettingService.getSubNode(tokenDto);
  }
}
