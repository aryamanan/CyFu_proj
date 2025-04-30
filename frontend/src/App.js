import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Box,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Avatar,
  Stack,
} from '@mui/material';
import axios from 'axios';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = {
      sender: 'user',
      text: inputValue,
    };

    setMessages((prevMessages) => [...prevMessages, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setLoading(true);
    
    try {
      const response = await axios.post('http://localhost:5005/webhooks/rest/webhook', {
        sender: "user",
        message: currentInput,
      });
      
      if (response.data && response.data.length > 0) {
        const botMessages = response.data.map(msg => ({
          sender: 'bot',
          text: msg.text,
        }));
        setMessages((prevMessages) => [...prevMessages, ...botMessages]);
      } else {
        setMessages((prevMessages) => [...prevMessages, {sender: 'bot', text: "Sorry, I didn't get a response."}]);
      }

    } catch (err) {
      console.error("Error sending message to Rasa:", err);
      setMessages((prevMessages) => [...prevMessages, {
        sender: 'bot',
        text: 'Error connecting to the bot. Please ensure the backend servers are running.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4, display: 'flex', flexDirection: 'column', height: '90vh' }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Recipe Chatbot
        </Typography>
        
        <Paper 
          elevation={3} 
          sx={{ 
            flexGrow: 1,
            p: 2, 
            mb: 2, 
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column-reverse'
          }}
        >
          <List sx={{ width: '100%' }}>
            <ListItem sx={{height: 0, padding: 0}} ref={messagesEndRef} />
            {messages.map((msg, index) => {
              const isUser = msg.sender === 'user';
              return (
                <ListItem key={index} sx={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
                  <Stack direction="row" spacing={1} alignItems="flex-start" sx={{ maxWidth: '75%' }}>
                    {!isUser && <Avatar sx={{ bgcolor: 'primary.main' }}><SmartToyIcon /></Avatar>}
                    <Paper 
                      elevation={1} 
                      sx={{
                        p: 1.5,
                        bgcolor: isUser ? 'primary.light' : 'grey.200',
                        borderRadius: isUser ? '20px 20px 5px 20px' : '20px 20px 20px 5px',
                      }}
                    >
                      <ListItemText 
                        primary={msg.text} 
                        primaryTypographyProps={{ style: { whiteSpace: 'pre-wrap' } }}
                      />
                    </Paper>
                     {isUser && <Avatar sx={{ bgcolor: 'secondary.main' }}><AccountCircleIcon /></Avatar>}
                  </Stack>
                </ListItem>
              );
            })}
          </List>
        </Paper>

        <Paper elevation={3} sx={{ p: 2 }}>
          <form onSubmit={handleSend}>
            <Stack direction="row" spacing={1}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Ask for a recipe..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={loading}
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                sx={{ minWidth: '80px'}}
              >
                {loading ? <CircularProgress size={24} /> : 'Send'}
              </Button>
            </Stack>
          </form>
        </Paper>
      </Box>
    </Container>
  );
}

export default App; 