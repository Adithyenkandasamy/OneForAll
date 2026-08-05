import { Search, Bell, Menu } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";

export function Header() {
  return (
    <header className="h-16 border-b bg-white flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-4">
        <button className="md:hidden">
          <Menu className="h-5 w-5" />
        </button>
        <div className="relative hidden sm:block w-96">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            type="search"
            placeholder="Search commands, machines, or alerts... (Ctrl+K)"
            className="pl-9 bg-gray-50/50 border-gray-200 focus-visible:ring-black h-9"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="relative text-gray-600 hover:text-black transition-colors">
          <Bell className="h-5 w-5" />
          <span className="absolute 0 right-0 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
        </button>
        <div className="h-8 w-px bg-gray-200 mx-2" />
        <Avatar className="h-8 w-8 cursor-pointer">
          <AvatarImage src="https://github.com/shadcn.png" />
          <AvatarFallback>AD</AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}
