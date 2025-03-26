import { Module } from '@nestjs/common';
import { CamsettingService } from './camsetting.service';
import { CamsettingController } from './camsetting.controller';
import { PythonScriptService } from './pythonscriptservice.service';
import { AuthModule } from 'src/auth/auth.module';
import { JwtModule } from '@nestjs/jwt';

@Module({
  imports: [AuthModule, JwtModule],
  providers: [CamsettingService, PythonScriptService],
  controllers: [CamsettingController],
})
export class CamsettingModule {}
