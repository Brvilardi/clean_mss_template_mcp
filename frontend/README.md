# re:Invent Chat Frontend

A React-based chat interface for the AWS re:Invent Planner Agent.

## Tech Stack

- **React 19** - Latest React with concurrent features
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **React Router v7** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Pre-built accessible components
- **Zustand** - Lightweight state management
- **AWS Amplify** - Authentication and API integration
- **Lucide React** - Icon library

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn components
│   │   ├── chat/            # Chat-specific components
│   │   ├── auth/            # Auth components
│   │   └── layout/          # Layout components
│   ├── pages/               # Page components
│   ├── store/               # Zustand stores
│   ├── services/            # API services
│   ├── types/               # TypeScript types
│   ├── utils/               # Utility functions
│   └── lib/                 # Shared libraries
├── public/                  # Static assets
└── amplify_outputs.json     # AWS configuration
```

## Getting Started

### Prerequisites

- Node.js 20.19+ or 22.12+
- npm 9+

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env.local` file with the following variables:

```env
VITE_APP_NAME="re:Invent Planner"
VITE_APP_DESCRIPTION="AI-powered conference planning assistant"
VITE_PRIMARY_COLOR="#FF9900"
```

## AWS Configuration

The application uses `amplify_outputs.json` for AWS configuration. This file should contain:

- Cognito user pool configuration
- API Gateway endpoint
- Authentication settings

## Adding shadcn/ui Components

To add new shadcn/ui components:

```bash
npx shadcn@latest add [component-name]
```

Example:
```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
```

## Features

- ✅ Secure authentication with AWS Cognito
- ✅ Custom user attributes (company name, website)
- ✅ Real-time chat interface
- ✅ Conversation history
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states
- ✅ Code splitting and lazy loading

## License

MIT
