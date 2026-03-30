/**
 * LeadOS Frontend Logger
 * Centralized utility for consistent, beautiful console logging.
 */

type LogLevel = 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';

const COLORS = {
  INFO:  '#3b82f6', // blue-500
  WARN:  '#f59e0b', // amber-500
  ERROR: '#ef4444', // red-500
  DEBUG: '#10b981', // emerald-500
};

class Logger {
  private prefix = '[LeadOS]';

  private log(level: LogLevel, message: string, data?: any) {
    const color = COLORS[level];
    const timestamp = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    console.log(
      `%c${this.prefix} %c[${timestamp}] %c${level}%c: ${message}`,
      `color: ${color}; font-weight: bold;`,
      `color: #6b7280;`, // gray-500
      `color: ${color}; font-weight: bold;`,
      `color: inherit;`,
      data !== undefined ? data : ''
    );
  }

  info(message: string, data?: any) {
    this.log('INFO', message, data);
  }

  warn(message: string, data?: any) {
    this.log('WARN', message, data);
  }

  error(message: string, data?: any) {
    this.log('ERROR', message, data);
  }

  debug(message: string, data?: any) {
    if (process.env.NODE_ENV === 'development') {
      this.log('DEBUG', message, data);
    }
  }
}

export const logger = new Logger();
