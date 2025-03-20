import Chat from './Chat'
import { useEffect } from 'react';
import { checkUser } from './helpers';


export default function Home() {
    useEffect(() => {
        checkUser();
      }, []);

  return (
    <div>
     <Chat /> 
    </div>
  );
}
