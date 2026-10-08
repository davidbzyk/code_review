import { readFile } from 'fs';

export interface Options {
  retries: number;
}

export function clamp(value: number, low: number, high: number): number {
  return Math.min(Math.max(value, low), high);
}

export class Registry {
  private items = new Map<string, number>();

  add(name: string, weight: number): void {
    this.items.set(name, clamp(weight, 0, 10));
  }

  total(): number {
    let sum = 0;
    for (const value of this.items.values()) {
      sum += value;
    }
    return sum;
  }
}

export const DEFAULT_OPTIONS: Options = { retries: 3 };
