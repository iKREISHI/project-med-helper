'use client'

import { useState, useRef, useCallback } from 'react';
import styles from './textArea.module.css'

interface ResizableTextareaProps {
  placeholder?: string;
  maxHeight?: number;
  onSend?: (message: string) => void;
}

export function ResizableTextarea({ 
  placeholder = "Введите ваш запрос...", 
  maxHeight = 200,
  onSend 
}: ResizableTextareaProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const autoResize = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.min(textarea.scrollHeight, maxHeight);
      textarea.style.height = `${newHeight}px`;
      textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
    }
  }, [maxHeight]);

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    autoResize();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend?.(value);
      setValue('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  return (
    <textarea
      ref={textareaRef}
      value={value}
      placeholder={placeholder}
      className={styles.ResizableTextarea}
      onInput={handleInput}
      onKeyPress={handleKeyPress}
      rows={1}
      style={{
        minHeight: '50px',
        maxHeight: `${maxHeight}px`
      }}
    />
  );
}