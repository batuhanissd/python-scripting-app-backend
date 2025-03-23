import { Module } from '@nestjs/common';
import { CamsettingService } from './camsetting.service';
import { CamsettingController } from './camsetting.controller';
import { PythonScriptService } from './pythonscriptservice.service';

@Module({
  providers: [CamsettingService, PythonScriptService],
  controllers: [CamsettingController],
})
export class CamsettingModule {}
