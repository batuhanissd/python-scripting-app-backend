import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { CamsettingModule } from './camsetting/camsetting.module';
import { PythonScriptService } from './camsetting/pythonscriptservice.service';

@Module({
  imports: [AuthModule, CamsettingModule],
  controllers: [AppController],
  providers: [AppService, PythonScriptService],
})
export class AppModule {}
